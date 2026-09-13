# GolfMate AI — Backend

FastAPI 기반 백엔드. Router → Service → Repository → AI Layer로 관심사를 분리하고,
DB 로직과 AI(LLM/LangGraph) 로직을 명확히 나눈다 (자세한 구조는 [`app/README.md`](app/README.md) 참고).

## 로컬 실행 (Docker 없이)

```bash
cd backend
python -m venv .venv
.venv\Scripts\activate        # Windows
pip install -r requirements-dev.txt

cp .env.example .env          # DATABASE_URL을 localhost 기준으로 수정

alembic upgrade head          # 테이블 생성
uvicorn app.main:app --reload --port 8010
```

## Docker Compose로 실행

프로젝트 루트에서:

```bash
docker compose up --build
docker compose exec backend alembic upgrade head
```

## 테스트

```bash
pytest
```

## 디렉터리

| 경로 | 역할 |
|---|---|
| `app/main.py` | FastAPI 앱 생성, CORS, 라우터 등록 |
| `app/core/` | 설정(config), DB 엔진/세션 |
| `app/models/` | SQLAlchemy ORM 모델 |
| `app/schemas/` | Pydantic 요청/응답 스키마 |
| `app/api/routers/` | HTTP 엔드포인트 (얇은 계층, 비즈니스 로직 없음) |
| `app/services/` | 비즈니스 로직 (Phase 2+) |
| `app/repositories/` | DB 접근 계층 (Phase 2+) |
| `app/ai/` | LangGraph/Agent/RAG (Phase 4+) |
| `alembic/` | DB 마이그레이션 |
| `tests/` | Pytest 테스트 |
