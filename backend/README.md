# GolfMate AI — Backend

FastAPI 기반 백엔드. Router → Service → Repository → AI Layer로 관심사를 분리하고,
DB 로직과 AI(LLM/LangGraph) 로직을 명확히 나눈다 (자세한 구조는 [`app/README.md`](app/README.md) 참고).

## 로컬 실행 (Docker 없이)

```bash
cd backend
python -m venv .venv
.venv\Scripts\activate        # Windows
pip install -r requirements-dev.txt

cp .env.example .env          # DATABASE_URL을 localhost 기준으로 수정, OPENROUTER_API_KEY 채우기

alembic upgrade head          # 테이블 생성
python -m app.seed_courses       # mock 골프장 3개 시드
python -m app.seed_demo_account  # 데모 계정(demo@golfmate.ai) + 라운드 8개 시드
uvicorn app.main:app --reload --port 8010
```

## Docker Compose로 실행

프로젝트 루트에서:

```bash
docker compose up --build
```

컨테이너 시작 시 마이그레이션, 코스 시드, 데모 계정 시드를 자동으로 실행한다
(`Dockerfile`의 CMD 참고 — 모두 멱등적이라 매번 실행해도 안전하다). 별도로 실행할 필요 없다.
로그인 화면의 "데모 계정으로 체험하기" 버튼이 이 계정(`demo@golfmate.ai`)으로 바로 로그인한다.

## Railway 배포

모노레포라 루트에서 자동 빌드가 안 되므로 `backend/`를 root로 CLI 업로드 배포한다:

```bash
railway up backend --path-as-root --service GolfMate --ci
railway variable set "DATABASE_URL=${{Postgres.DATABASE_URL}}" --service GolfMate
railway variable set "JWT_SECRET_KEY=<openssl rand -hex 32 등으로 생성>" --service GolfMate
railway variable set "JWT_ALGORITHM=HS256" --service GolfMate
railway variable set "JWT_EXPIRE_MINUTES=1440" --service GolfMate
railway variable set "CORS_ORIGINS=<프론트 공개 URL>" --service GolfMate
railway variable set "OPENROUTER_API_KEY=<https://openrouter.ai/keys 에서 발급>" --service GolfMate
railway domain --service GolfMate --port 8000
```

컨테이너 부팅 시 `Dockerfile`의 CMD가 마이그레이션/코스 시드/데모 계정 시드를 자동 실행하므로
별도 원격 명령이 필요 없다.

## 테스트

DB가 필요 없는 테스트(`test_health.py`)는 로컬 venv에서 바로 실행된다:

```bash
pytest
```

`test_auth.py`처럼 실제 PostgreSQL 연결이 필요한 테스트는 Docker 컨테이너 안에서 실행한다
(Windows 로컬 venv의 psycopg2가 환경변수를 파싱하다 `UnicodeDecodeError`를 내는 경우가 있어,
컨테이너 안에서 실행하는 쪽이 더 안정적이다):

```bash
docker compose exec backend pip install pytest httpx   # requirements-dev만 추가 설치
docker compose exec backend pytest
```

## 디렉터리

| 경로 | 역할 |
|---|---|
| `app/main.py` | FastAPI 앱 생성, CORS, 라우터 등록 |
| `app/core/` | 설정(config), DB 엔진/세션 |
| `app/models/` | SQLAlchemy ORM 모델 |
| `app/schemas/` | Pydantic 요청/응답 스키마 |
| `app/api/routers/` | HTTP 엔드포인트 (얇은 계층, 비즈니스 로직 없음) |
| `app/services/` | 비즈니스 로직 (인증, 라운드, 통계 계산 등) |
| `app/repositories/` | DB 접근 계층 |
| `app/seed_courses.py` | mock 골프장 3개 시드 스크립트 |
| `app/seed_demo_account.py` | 데모 계정 + 라운드 8개 시드 스크립트 |
| `app/ai/` | LangGraph AI Coach (Phase 4), RAG/Caddie 등은 Phase 5+ |
| `alembic/` | DB 마이그레이션 |
| `tests/` | Pytest 테스트 |
