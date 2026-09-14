"""GolfKnowledge 테이블 — RAG용 골프 지식(규칙/스윙/퍼팅/코스 매니지먼트/에티켓).

사용자 개인 데이터(rounds, holes 등 일반 테이블)와 분리된 지식 데이터로,
`embedding` 컬럼(pgvector)을 통해 질문과 의미적으로 가까운 항목을 검색한다
(app/ai/rag/retriever.py). 이 테이블의 내용은 app/ai/rag/knowledge_data.py에서
직접 작성한 일반 골프 지식이며, LLM이 임의로 채우지 않는다.
"""
from datetime import datetime

from pgvector.sqlalchemy import Vector
from sqlalchemy import DateTime, String, Text, func
from sqlalchemy.orm import Mapped, mapped_column

from app.models.base import Base

# intfloat/multilingual-e5-small의 출력 차원. 임베딩 모델을 바꾸면 이 값과
# app/ai/rag/embeddings.py, 그리고 마이그레이션의 Vector(...) 차원도 함께 바꿔야 한다.
EMBEDDING_DIM = 384


class GolfKnowledge(Base):
    __tablename__ = "golf_knowledge"

    id: Mapped[int] = mapped_column(primary_key=True)
    category: Mapped[str] = mapped_column(String(50), nullable=False)
    title: Mapped[str] = mapped_column(String(200), nullable=False, unique=True)
    content: Mapped[str] = mapped_column(Text, nullable=False)
    embedding: Mapped[list[float]] = mapped_column(Vector(EMBEDDING_DIM), nullable=False)

    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
