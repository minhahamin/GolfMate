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
├── prompts/coach/
│   └── system.py         # Coach 프롬프트 템플릿 (Role→Goal→Data→Rules→Format)
└── coach/
    ├── state.py           # GolfCoachState (TypedDict)
    ├── graph.py           # Coach LangGraph 정의 + 실행 함수
    └── parser.py          # LLM 응답을 5개 섹션으로 텍스트 파싱
```

## Coach Graph (Phase 4, 구현 완료)

```text
START
 → intent_analyzer         (빈 질문에 기본 질문 채우기 — 향후 다중 의도 라우팅 확장 지점)
 → get_golfer_profile       (golfer_profile_repository 재사용, LLM 없음)
 → get_recent_rounds        (round_repository.list_recent_by_user 재사용, LLM 없음)
 → statistics_analyzer      (Phase 3 statistics_service.compute_statistics_summary 재사용,
                              LLM 없음 — 순수 계산)
 → weakness_and_strategy    (유일한 LLM 호출. §14 프롬프트로 5개 섹션을 한 번에 생성)
 → recommendation_validator (규칙 기반: 응답이 비어있으면 폴백 메시지로 교체)
 → END
```

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

## 예정 구조 (Phase 5+)

- **RAG** (Phase 5): 골프 지식(규칙/용어/스윙/코스 매니지먼트)을 pgvector에 임베딩,
  개인 데이터(PostgreSQL)와 지식 데이터(pgvector)를 분리 관리. `app/ai/rag/`
- **Diary Graph** (Phase 6): STT → Diary Extraction → Round Matching → Emotion/Event
  Analysis → Diary Generation
- **Course Recommendation Graph** (Phase 7): Preference Analyzer → Course Search Tool →
  Filter → Recommendation Agent → Ranking (실존하지 않는 골프장을 LLM이 만들어내지 않도록,
  후보는 항상 DB/외부 API에서 가져온 것만 사용)
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
