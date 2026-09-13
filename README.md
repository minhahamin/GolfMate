# GolfMate AI

> 골프 라운드 데이터를 지속적으로 축적하고, 이를 기반으로 AI 코치·AI 캐디·골프장 추천·
> AI 골프일기·내기 분석을 제공하는 **AI 골프 플랫폼**. 단발성 응답을 만드는 챗봇이 아니라,
> 사용자 데이터가 쌓일수록 더 정확해지는 서비스를 목표로 한 개인 포트폴리오 프로젝트입니다.

**🔗 라이브 데모**: https://golfmate-frontend-production.up.railway.app
(로그인 화면의 "데모 계정으로 체험하기" 버튼으로 가입 없이 바로 둘러볼 수 있습니다 —
라운드 8개가 미리 채워져 있어 통계/차트가 바로 보입니다.)

## 왜 이 프로젝트인가

"LLM API를 감싼 챗봇"은 만들기 쉽지만 실제 제품 가치를 증명하기 어렵습니다. GolfMate AI는
LLM 애플리케이션을 실제 서비스 아키텍처 안에서 다루는 것을 목표로 합니다 — 계산 가능한 것은
코드가 처리하고, LLM은 판단과 자연어 설명에만 쓰는 원칙을 지킵니다.

```text
정확한 계산 → 일반 코드 / SQL     예) 평균 타수, 퍼팅 평균, 내기 정산, 거리 계산
데이터 조회 → Tool                예) 골퍼 프로필, 최근 라운드, 코스 정보, 날씨
지식 검색   → RAG (pgvector)      예) 골프 규칙, 스윙/퍼팅 이론, 코스 매니지먼트
판단/설명   → LLM (LangGraph)     예) 약점 분석, 공략 전략, 추천 사유, 일기 생성
```

## 전체 아키텍처

```text
        User
         │
      React (TS, Vite, Tailwind, React Query)
         │  axios (REST)
      FastAPI  ── Router → Service → Repository ──┐
         │                                        │
         │                                   PostgreSQL
         │                                  (사용자 데이터)
         ▼
      LangGraph (Agent / Tool Calling / RAG)
         │                                   pgvector
         ▼                                (골프 지식 데이터)
        LLM
         │
      Validation (환각 방지, 스키마 검증)
         │
      FastAPI → React
```

- **사용자 개인 데이터**(라운드 기록, 프로필, 내기 결과 등)와 **골프 지식 데이터**(규칙, 이론,
  코스 매니지먼트)는 저장소 수준에서 분리됩니다 — 전자는 PostgreSQL 일반 테이블, 후자는
  pgvector 임베딩입니다 (Phase 5에서 도입).
- 모든 AI 기능은 LangGraph의 명시적인 State Graph로 구현되어, 각 단계(노드)가 무엇을 하는지
  추적 가능합니다. Langfuse로 모든 LLM 호출의 Trace/Token/Latency를 기록합니다 (Phase 10).

## 기술 스택

| 영역 | 기술 |
|---|---|
| Frontend | React, TypeScript, Vite, React Router, Tailwind CSS, Axios, TanStack Query, Recharts |
| Backend | Python 3.12, FastAPI, Pydantic, SQLAlchemy, Alembic, PostgreSQL, JWT |
| AI | LangChain, LangGraph, Langfuse, LLM API, Embedding Model, pgvector, RAG, Tool Calling |
| Voice | STT / TTS (외부 API 우선 적용, 교체 가능한 인터페이스로 분리) |
| Infra | Docker, Docker Compose, Nginx(배포 단계에서 도입) |

## 데이터 모델 (개요)

```text
users ──1:1── golfer_profiles
users ──1:N── rounds ──1:N── holes ──1:N── shots
courses ──1:N── course_holes
users ──1:N── diaries
users ──N:M── groups (group_members) ──1:N── bets ──1:N── bet_results
users ──1:N── ai_sessions ──1:N── ai_messages / ai_recommendations
golf_knowledge (pgvector, RAG 전용)
```

`users`, `golfer_profiles`, `courses`, `course_holes`, `rounds`, `holes`까지 구현되어
있습니다. 나머지 테이블은 해당 기능이 구현되는 Phase에서 순차적으로 추가됩니다.

## 개발 로드맵

| Phase | 내용 | 상태 |
|---|---|---|
| 1 | 프로젝트 기본 구조 (React+FastAPI+PostgreSQL+Docker) | ✅ 완료 |
| 2 | 회원가입/로그인 (JWT), Golfer Profile | ✅ 완료 |
| 3 | 골프 데이터 (Course/Round/Hole/Statistics) — AI 없이 먼저 동작 | ✅ 완료 |
| 4 | AI Coach (LangChain/LangGraph) | 예정 |
| 5 | RAG (골프 지식, pgvector) | 예정 |
| 6 | AI Golf Diary (STT + Structured Extraction) | 예정 |
| 7 | 골프장 추천 (실데이터 연동) | 예정 |
| 8 | AI Caddie (Course/Hole/Weather/Risk) | 예정 |
| 9 | Golf Bet Analysis (그룹/정산/AI Commentary) | 예정 |
| 10 | Langfuse (Tracing/Prompt Management/Evaluation) | 예정 |

## 현재 상태 (Phase 3까지)

- FastAPI 앱과 PostgreSQL이 Docker Compose(로컬)와 Railway(배포)로 연결되고,
  `GET /api/health/db`가 실제 DB 커넥션을 확인합니다.
- Router → Service → Repository → AI Layer로 이어지는 백엔드 레이어 구조와, 이후 AI 기능이
  들어갈 `app/ai/` 자리를 미리 스캐폴딩해두었습니다 (자세한 설계 메모는
  [`backend/app/ai/README.md`](backend/app/ai/README.md) 참고).
- 회원가입/로그인이 JWT(`pyjwt`) + 비밀번호 해싱(`bcrypt`)으로 동작합니다. 가입 시 빈
  `GolferProfile`이 함께 생성되고, 로그인한 사용자만 `/api/users/me`, `/api/rounds/*` 등
  본인 데이터에만 접근할 수 있습니다 (`get_current_user` 의존성이 유일한 인증 관문 — 다른
  사용자의 라운드는 403이 아닌 404로 응답해 존재 자체를 숨긴다).
- 골프장(Course/CourseHole)과 라운드(Round/Hole) CRUD가 동작합니다. 라운드 등록 시 홀별
  상세를 입력하면 총타수를 서버가 홀 점수 합으로 계산하고, `statistics_service.py`가 순수
  Python으로 평균 스코어·퍼팅·페어웨이·GIR 등을 계산합니다 (LLM 호출 없음 — 이 계산 로직을
  Phase 4 AI Coach가 그대로 재사용할 예정).
- React 앱은 `localStorage`에 JWT를 저장하고 axios 인터셉터로 자동 첨부합니다. `/login`,
  `/register`, 보호된 `/dashboard`(통계 요약+Recharts 트렌드 차트), `/rounds`,
  `/rounds/new`(18홀 상세 입력 지원), `/rounds/:id`(분석 통계), `/courses`, `/profile`이
  동작합니다. 미인증 접근은 `/login`으로 리다이렉트됩니다.
- 회원가입 없이 바로 체험할 수 있는 데모 계정(`demo@golfmate.ai`, 라운드 8개 미리 시드됨)이
  로그인 화면에 있습니다.

## 배포 (Railway)

백엔드/프론트엔드/PostgreSQL을 별도 서비스 3개로 분리 배포했습니다 (모노레포라 루트에서
자동 빌드가 안 되므로, 각 서비스는 `backend/`, `frontend/`를 루트로 CLI(`railway up --path-as-root`)로
배포합니다).

| 서비스 | 내용 |
|---|---|
| `GolfMate` (backend) | `backend/Dockerfile` — 부팅 시 마이그레이션+코스+데모계정 시드 자동 실행 |
| `golfmate-frontend` | `frontend/Dockerfile`(운영용, nginx 정적 서빙) — 로컬 개발은 `Dockerfile.dev` 사용 |
| `Postgres` | Railway 플러그인 |

프론트는 빌드 시점에 `VITE_API_BASE_URL`을 백엔드 공개 URL로 굽고, 백엔드 `CORS_ORIGINS`는
프론트 공개 URL을 허용하도록 설정되어 있습니다.

## 실행 방법

### Docker Compose (권장)

```bash
cp .env.example .env
cp backend/.env.example backend/.env
cp frontend/.env.example frontend/.env

docker compose up --build
docker compose exec backend alembic upgrade head
```

- Frontend: http://localhost:5180
- Backend: http://localhost:8010/api/health
- Backend API 문서 (Swagger): http://localhost:8010/docs

> 포트를 8010/5180처럼 비표준으로 잡은 이유: 로컬에 다른 프로젝트가 이미 Vite/FastAPI
> 기본 포트(5173/8000)를 쓰고 있으면, 브라우저가 `localhost`를 IPv6(`::1`)로 먼저 해석하면서
> 엉뚱한 서버로 연결되는 경우가 있다. `.env`의 `FRONTEND_PORT`/`BACKEND_PORT`로 언제든 바꿀 수 있다.

### 개별 실행 (Docker 없이)

각 부분의 상세 실행 방법은 [`backend/README.md`](backend/README.md),
[`frontend/README.md`](frontend/README.md)를 참고하세요.

## 프로젝트 구조

```text
GolfMate/
├── backend/     — FastAPI (Router/Service/Repository/AI Layer)
└── frontend/    — React + TypeScript + Vite
```

폴더마다 README.md로 해당 디렉터리의 역할과 확장 계획을 문서화했습니다.

## 설계 원칙

1. LLM에게 모든 것을 맡기지 않는다 — 계산은 코드, 판단/설명은 LLM.
2. LLM은 DB에 직접 접근하지 않고 반드시 Tool을 통해서만 데이터를 받는다.
3. 사용자 개인 데이터(PostgreSQL)와 골프 지식(pgvector)을 분리한다.
4. 골프장 등 실존 정보는 LLM이 지어내지 않고, 항상 실제 DB/외부 API 후보 중에서만 추천한다.
5. 내기 금액/정산 같은 금전 계산은 LLM이 아닌 Python 코드가 담당하고 별도로 테스트한다.
6. API Key/DB 자격증명은 코드에 하드코딩하지 않고 환경변수로만 관리한다.
7. 사용자 A는 사용자 B의 데이터를 절대 조회할 수 없다.
