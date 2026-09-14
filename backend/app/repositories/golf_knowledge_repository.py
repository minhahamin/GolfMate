"""GolfKnowledge 테이블 접근 전용 계층."""
from sqlalchemy.orm import Session

from app.models.golf_knowledge import GolfKnowledge


def get_by_title(db: Session, title: str) -> GolfKnowledge | None:
    return db.query(GolfKnowledge).filter(GolfKnowledge.title == title).first()


def search_similar(db: Session, query_embedding: list[float], top_k: int = 3) -> list[GolfKnowledge]:
    return (
        db.query(GolfKnowledge)
        .order_by(GolfKnowledge.embedding.cosine_distance(query_embedding))
        .limit(top_k)
        .all()
    )
