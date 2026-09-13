# ai/ — LLM / LangGraph / RAG / Agent 계층

Phase 1에는 코드가 없다. 이 파일은 Phase 4부터 이 폴더를 채울 때 참고할 설계 메모다.

## 원칙

LLM에게 모든 작업을 맡기지 않는다. 정확한 계산(평균 타수, 퍼팅 평균, 거리 계산, 내기 정산 등)은
`app/services`의 일반 코드가 담당하고, **판단과 자연어 생성만 LLM이 담당**한다. LLM은 절대
DB에 직접 접근하지 않으며, 반드시 Tool을 통해 데이터를 받는다.

```text
User → React → FastAPI → LangGraph → Agent/Tool/RAG → LLM → Validation → FastAPI → React
```

## 예정 구조

```text
app/ai/
├── graphs/          # LangGraph StateGraph 정의 (coach_graph.py, caddie_graph.py, ...)
├── nodes/           # 각 그래프의 노드 함수 (단일 책임)
├── tools/           # LLM이 호출하는 Tool (get_golfer_profile, search_courses, ...)
├── prompts/         # coach/caddie/course/diary/bet 별 프롬프트 (Role→Goal→Data→Rules→Format)
├── rag/             # 문서 로더, chunking, embedding, retriever
└── llm/             # LLM 클라이언트 초기화, Langfuse 연동
```

## 그래프별 개요 (Phase별 구현 예정)

- **Coach Graph** (Phase 4): Intent Analyzer → Get Profile → Get Recent Rounds →
  Statistics Analyzer → Weakness Analyzer → Strategy Generator → Validator
- **RAG** (Phase 5): 골프 지식(규칙/용어/스윙/코스 매니지먼트)을 pgvector에 임베딩,
  개인 데이터(PostgreSQL)와 지식 데이터(pgvector)를 분리 관리
- **Diary Graph** (Phase 6): STT → Diary Extraction → Round Matching → Emotion/Event
  Analysis → Diary Generation
- **Course Recommendation Graph** (Phase 7): Preference Analyzer → Course Search Tool →
  Filter → Recommendation Agent → Ranking (실존하지 않는 골프장을 LLM이 만들어내지 않도록,
  후보는 항상 DB/외부 API에서 가져온 것만 사용)
- **Caddie Graph** (Phase 8): Get Profile → Get Course/Hole → Get Weather → Hole Analysis →
  Risk Analysis → Club Strategy → Validator
- **Bet Analysis Graph** (Phase 9): Get Group/Members/Rounds → Statistics → Bet Rule Engine
  (Python 정산) → AI Commentary (LLM은 설명만, 금액 계산은 하지 않음)
- **Langfuse** (Phase 10): 모든 그래프의 Trace/Span/Generation/Token/Latency를 추적

## State 설계 원칙

그래프마다 별도의 `TypedDict` State를 정의한다 (예: `GolfCoachState`). 하나의 거대한 State에
모든 그래프의 데이터를 몰아넣지 않는다.
