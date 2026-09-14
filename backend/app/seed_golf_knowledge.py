"""골프 지식(RAG) 시드 스크립트.

app/ai/rag/knowledge_data.py에 정리된 항목을 임베딩해 golf_knowledge 테이블에 넣는다.
이미 같은 제목의 항목이 있으면 건너뛴다 (여러 번 실행해도 안전).

실행:
    docker compose exec backend python -m app.seed_golf_knowledge
"""
from app.ai.rag.embeddings import embed_passages
from app.ai.rag.knowledge_data import GOLF_KNOWLEDGE
from app.core.database import SessionLocal
from app.models.golf_knowledge import GolfKnowledge
from app.repositories import golf_knowledge_repository


def run() -> None:
    db = SessionLocal()
    try:
        entries = [
            entry for entry in GOLF_KNOWLEDGE if golf_knowledge_repository.get_by_title(db, entry["title"]) is None
        ]
        skipped = len(GOLF_KNOWLEDGE) - len(entries)
        if skipped:
            print(f"이미 존재함, 건너뜀: {skipped}건")

        if not entries:
            return

        embeddings = embed_passages([entry["content"] for entry in entries])
        for entry, embedding in zip(entries, embeddings):
            db.add(
                GolfKnowledge(
                    category=entry["category"],
                    title=entry["title"],
                    content=entry["content"],
                    embedding=embedding,
                )
            )
            print(f"생성됨: [{entry['category']}] {entry['title']}")

        db.commit()
    finally:
        db.close()


if __name__ == "__main__":
    run()
