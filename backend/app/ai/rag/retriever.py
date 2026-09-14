"""골프 지식 검색(RAG). 개인 데이터(rounds 등)와 분리된 지식 데이터(golf_knowledge)에서
질문과 의미적으로 가까운 항목을 찾아온다. LLM은 이 결과만 근거로 규칙/이론을 설명한다.
"""
from sqlalchemy.orm import Session

from app.ai.rag.embeddings import embed_query
from app.models.golf_knowledge import GolfKnowledge
from app.repositories import golf_knowledge_repository


def retrieve_knowledge(db: Session, query: str, top_k: int = 3) -> list[GolfKnowledge]:
    if not query.strip():
        return []
    query_embedding = embed_query(query)
    return golf_knowledge_repository.search_similar(db, query_embedding, top_k=top_k)
