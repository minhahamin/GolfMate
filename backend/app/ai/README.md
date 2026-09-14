# ai/ — LLM / LangGraph / RAG / Agent 계층

## 원칙

LLM에게 모든 작업을 맡기지 않는다. 정확한 계산(평균 타수, 퍼팅 평균, 거리 계산, 내기 정산 등)은
`app/services`의 일반 코드가 담당하고, **판단과 자연어 생성만 LLM이 담당**한다. LLM은 절대
DB에 직접 접근하지 않으며, 이 그래프는 서비스/레포지토리 함수를 직접 호출해 데이터를 가져온다.

```text
User → React → FastAPI → LangGraph → Agent/Tool/RAG → LLM → Validation → FastAPI → React
```

## 현재 구조

```text
app/ai/
├── llm/
│   └── client.py         # OpenRouter(OpenAI 호환 API)로 ChatOpenAI 구성
├── stt/
│   └── transcriber.py     # 로컬 faster-whisper로 음성 → 텍스트 전사 (Phase 6)
├── prompts/
│   ├── coach/system.py     # Coach 프롬프트 템플릿 (Role→Goal→Data→Rules→Format)
│   ├── diary/system.py     # Diary 프롬프트 템플릿 (Phase 6)
│   └── recommend/system.py # 골프장 추천 프롬프트 템플릿 (Phase 7)
├── rag/
│   ├── embeddings.py      # 로컬 sentence-transformers 임베딩 (multilingual-e5-small)
│   ├── knowledge_data.py  # 시드용 골프 지식 원본 데이터 (규칙/스윙/퍼팅/코스매니지먼트/에티켓)
│   └── retriever.py       # 질문 임베딩 → golf_knowledge_repository 검색
├── coach/
│   ├── state.py           # GolfCoachState (TypedDict)
│   ├── graph.py           # Coach LangGraph 정의 + 실행 함수
│   └── parser.py          # LLM 응답을 5개 섹션으로 텍스트 파싱
├── diary/
│   ├── state.py           # DiaryState (TypedDict) — Phase 6
│   ├── graph.py           # Diary LangGraph 정의 + 실행 함수 — Phase 6
│   └── parser.py          # LLM 응답을 6개 섹션(5개 필드+매칭라운드)으로 텍스트 파싱 — Phase 6
└── recommend/
    ├── state.py           # RecommendState (TypedDict) — Phase 7
    ├── graph.py           # 골프장 추천 LangGraph 정의 + 실행 함수 — Phase 7
    └── parser.py          # LLM 응답을 순위별 추천 목록으로 텍스트 파싱 — Phase 7
```

## Coach Graph (Phase 4~5, 구현 완료)

```text
START
 → intent_analyzer         (빈 질문에 기본 질문 채우기 — 향후 다중 의도 라우팅 확장 지점)
 → get_golfer_profile       (golfer_profile_repository 재사용, LLM 없음)
 → get_recent_rounds        (round_repository.list_recent_by_user 재사용, LLM 없음)
 → retrieve_golf_knowledge  (Phase 5: pgvector에서 질문과 관련된 골프 지식 검색, LLM 없음)
 → statistics_analyzer      (Phase 3 statistics_service.compute_statistics_summary 재사용,
                              LLM 없음 — 순수 계산)
 → weakness_and_strategy    (유일한 LLM 호출. §14 프롬프트로 5개 섹션을 한 번에 생성)
 → recommendation_validator (규칙 기반: 응답이 비어있으면 폴백 메시지로 교체)
 → END
```

## RAG (Phase 5, 구현 완료)

- 사용자 개인 데이터(PostgreSQL 일반 테이블)와 골프 지식(pgvector 임베딩)을 테이블 수준에서
  분리했다 — `golf_knowledge` 테이블만 `embedding` 컬럼(pgvector `Vector(384)`)을 가진다.
- 임베딩은 OpenRouter의 임베딩 API 없이, 로컬 `sentence-transformers`
  (`intfloat/multilingual-e5-small`)로 API 키 없이 생성한다 — LLM도 무료 모델만 쓰는
  기존 원칙과 일관된 선택이다.
- `app/seed_golf_knowledge.py`가 `knowledge_data.py`의 항목을 임베딩해 시드한다 (Dockerfile
  CMD에서 부팅 시 자동 실행, 제목 중복이면 건너뛰는 멱등적 스크립트).
- Coach 그래프의 `retrieve_golf_knowledge` 노드가 질문을 임베딩해 코사인 거리 기준 상위 3개
  지식 항목을 가져오고, 프롬프트의 "관련 골프 지식" 섹션에 그대로 넣는다. 프롬프트 규칙에
  "이 섹션에 없는 규칙/이론을 지어내지 말 것"을 명시해, LLM이 검증되지 않은 골프 규칙을
  만들어내지 않도록 한다.
- 데이터 규모가 수십 건이라 ivfflat/hnsw 같은 근사 인덱스 없이 정확 코사인 거리 정렬만
  사용한다. 항목이 크게 늘어나면 인덱스를 추가하면 된다.

**설계 결정**:
- 마스터 스펙 §11의 "약점 분석"과 "전략 생성"을 노드 하나(`weakness_and_strategy`)로
  합쳤다 — §14의 실제 예시 프롬프트도 원래 5개 섹션을 한 번에 요구하고, 무료 LLM의
  rate limit 부담을 줄이기 위함이다.
- 라운드가 하나도 없으면 LLM을 호출하지 않고 "데이터 없음" 안내를 바로 반환한다.
- LLM 호출 실패/예외 시 폴백 메시지로 응답하고 500을 던지지 않는다 (§29).
- 응답 파싱은 JSON/함수호출이 아니라 `[헤더]` 텍스트 분리 방식이다 — 무료 모델은 언제든
  교체될 수 있어서, 모델별 구조화 출력 지원 여부에 의존하지 않는 가장 견고한 방식을 골랐다.
- Tool Calling(§16)은 아직 본격적으로 쓰지 않는다 — 지금은 고정된 파이프라인이라 LLM이
  동적으로 도구를 선택할 필요가 없다. Phase 8(Caddie)처럼 더 에이전틱한 기능이 필요할 때
  LangChain `@tool`로 이 서비스 함수들을 감싸면 된다.
- Langfuse(§18)는 로드맵대로 Phase 10에서 정식 도입한다. 지금은 `logging`으로 모델명/
  지연시간/성공여부만 남긴다 (`app/ai/coach/graph.py`의 `logger.info`).

**알려진 한계**: `OPENROUTER_MODEL` 기본값(`nvidia/nemotron-3-super-120b-a12b:free`)은
가끔 한국어 답변에 다른 언어 단어가 한두 개 섞여 나올 수 있다 (무료 모델의 특성). 프롬프트에
"한국어로만 작성" 규칙을 넣어 완화했지만 완전히 없애지는 못한다. 더 안정적인 무료 모델이
나오면 `OPENROUTER_MODEL` 환경변수만 바꾸면 된다.

로컬 개발(Docker Compose)과 Railway 배포 모두 `pgvector/pgvector:pg16` 이미지를 쓴다. Railway의
기본 Postgres 플러그인에는 pgvector가 없어서, `golfmate-pgvector`라는 별도 서비스를
`pgvector/pgvector:pg16` 이미지로 새로 만들고 백엔드 `DATABASE_URL`을 그쪽으로 옮겼다
(루트 [`README.md`](../../../README.md)의 "배포 (Railway)" 절 참고). 볼륨을 데이터 디렉터리
루트(`/var/lib/postgresql/data`)에 직접 마운트하면 `lost+found` 디렉터리 때문에 `initdb`가
실패하므로, 볼륨은 `/pgdata`에 마운트하고 `PGDATA=/pgdata/pgdata`(하위 디렉터리)로 지정했다.

## Diary Graph (Phase 6, 구현 완료)

```text
START
 → get_recent_rounds  (round_repository.list_recent_by_user 재사용, Coach와 동일 함수, LLM 없음)
 → diary_generation    (유일한 LLM 호출 — 감정/사건 정리 + 라운드 매칭 + 일기 생성을 한 번에)
 → diary_validator     (규칙 기반: 응답이 비어있으면 폴백, 후보 목록에 없는 round_id는 버림)
 → END
```

- STT(음성 → 텍스트)는 이 그래프에 포함하지 않는다. 오디오 디코딩 실패는 "AI 판단 실패"가
  아니라 "사용자 입력 자체가 유효하지 않음"이라 Coach 스타일 LLM 폴백과 성격이 달라서다 —
  `app/services/diary_service.py`가 그래프 호출 전에 먼저 처리해 실패 시 422로 끊는다.
- STT는 과금 없이 API 키 없이 쓸 수 있도록, RAG의 로컬 임베딩 모델과 같은 원칙으로
  로컬 `faster-whisper`(PyTorch 불필요, CTranslate2 기반)를 쓴다 (`app/ai/stt/transcriber.py`).
  원본 오디오는 전사 직후 폐기하고 서버에 저장하지 않는다.
- `diary_generation`이 최근 라운드 후보 목록(id 포함)을 프롬프트에 주고, LLM이 그중 하나를
  고르거나 "없음"을 답하게 한다 — 원칙("실존 정보는 LLM이 지어내지 않고 항상 실제 DB 후보
  중에서만 선택")을 그대로 적용. `diary_validator`가 LLM이 후보에 없는 id를 답해도(환각)
  최종적으로 걸러낸다.
- 사용자가 폼에서 직접 라운드를 선택했다면(`round_id_hint`) LLM의 매칭 결과 대신 그 값을
  그대로 신뢰한다.
- Coach와 동일한 LLM 클라이언트(`get_coach_llm()`)를 그대로 재사용한다 — 별도 클라이언트를
  만들지 않았다.

## Course Recommendation Graph (Phase 7, 구현 완료)

```text
START
 → get_golfer_profile        (golfer_profile_repository 재사용, LLM 없음)
 → search_candidate_courses  (course_repository.search — region/difficulty/max_budget으로
                               필터링된 실제 DB 후보만 가져온다, LLM 없음)
 → recommendation_generation (유일한 LLM 호출 — 후보 중 최대 3곳 순위/이유 생성)
 → recommendation_validator  (규칙 기반: 후보 목록에 없는 id는 버림 — 환각 방지)
 → END
```

- 실데이터 연동을 "실제 외부 유료/가입 API"가 아니라 "실제 DB 레코드 기반 검색"으로
  구현했다 — 무료로 쓸 수 있는 신뢰할 만한 국내 골프장 API를 확보하지 못해, 대신
  `courses` 테이블을 10곳으로 확장하고 `difficulty`/`green_fee_avg`/`tags` 필드를 추가해
  진짜 필터링 가능한 후보 검색을 만들었다 (`app/seed_courses.py`). 나중에 공공데이터포털
  같은 실제 API 키가 생기면 `course_repository.search`의 데이터 소스만 교체하면 된다.
- Coach/Diary와 같은 환각 방지 원칙: LLM은 `search_candidate_courses`가 이미 필터링한
  후보 중에서만 고르고, `recommendation_validator`가 후보 목록에 없는 id를 최종적으로
  한 번 더 걸러낸다.
- 후보가 하나도 없으면(필터 조건이 너무 좁음) LLM을 호출하지 않고 바로 안내 문구를
  반환한다.
- Coach와 동일한 LLM 클라이언트(`get_coach_llm()`)를 재사용한다.

## 예정 구조 (Phase 8+)

- **Caddie Graph** (Phase 8): Get Profile → Get Course/Hole → Get Weather → Hole Analysis →
  Risk Analysis → Club Strategy → Validator — 여기서 본격적인 Tool Calling 도입 예정
- **Bet Analysis Graph** (Phase 9): Get Group/Members/Rounds → Statistics → Bet Rule Engine
  (Python 정산) → AI Commentary (LLM은 설명만, 금액 계산은 하지 않음)
- **Langfuse** (Phase 10): 모든 그래프의 Trace/Span/Generation/Token/Latency를 추적

## State 설계 원칙

그래프마다 별도의 `TypedDict` State를 정의한다 (예: `GolfCoachState`). 하나의 거대한 State에
모든 그래프의 데이터를 몰아넣지 않는다.

## LangGraph 사용 시 주의

이 프로젝트가 쓰는 `langgraph==0.2.53`에서는 노드 함수가 **빈 dict(`{}`)를 반환하면
`InvalidUpdateError`가 난다** (아무 키도 없으면 "갱신할 게 없다"고 판단해 에러를 던짐).
아무 것도 갱신하지 않는 pass-through 노드를 만들 때는 최소 1개 키를 자기 자신의 값으로라도
반환해야 한다 (`graph.py`의 `intent_analyzer`, `recommendation_validator` 참고).
