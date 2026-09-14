"""FastAPI 애플리케이션 엔트리포인트.

여기서는 앱 인스턴스 생성, 미들웨어 설정, 라우터 등록만 담당한다.
비즈니스 로직은 services/, DB 접근은 repositories/, AI 로직은 ai/ 에 둔다.
"""
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.routers import auth, caddie, coach, courses, diaries, health, recommend, rounds, users
from app.core.config import get_settings

settings = get_settings()

app = FastAPI(title="GolfMate AI API", version="0.1.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origin_list,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(health.router, prefix="/api")
app.include_router(auth.router, prefix="/api")
app.include_router(users.router, prefix="/api")
app.include_router(courses.router, prefix="/api")
app.include_router(rounds.router, prefix="/api")
app.include_router(coach.router, prefix="/api")
app.include_router(diaries.router, prefix="/api")
app.include_router(recommend.router, prefix="/api")
app.include_router(caddie.router, prefix="/api")


@app.get("/")
def root() -> dict[str, str]:
    return {"service": "GolfMate AI API", "status": "running"}
