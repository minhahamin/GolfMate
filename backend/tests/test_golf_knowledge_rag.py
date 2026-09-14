"""RAG(골프 지식) 임베딩/검색 테스트.

sentence-transformers 모델은 실제로 로드해서 사용한다 (LLM 호출과 달리 임베딩은
API 키/네트워크 비용이 없는 로컬 연산이라 모킹하지 않는다). 첫 실행 시 HuggingFace Hub에서
모델을 내려받으므로 인터넷 연결이 필요하다.
"""
import uuid

from app.ai.rag.embeddings import EMBEDDING_MODEL_NAME, embed_passage, embed_query
from app.ai.rag.retriever import retrieve_knowledge
from app.core.database import SessionLocal
from app.models.golf_knowledge import EMBEDDING_DIM, GolfKnowledge


def _seed_knowledge(category: str, title: str, content: str) -> None:
    db = SessionLocal()
    try:
        db.add(
            GolfKnowledge(
                category=category,
                title=title,
                content=content,
                embedding=embed_passage(content),
            )
        )
        db.commit()
    finally:
        db.close()


def test_embed_query_and_passage_return_expected_dimension():
    query_vector = embed_query("퍼팅을 잘하는 방법")
    passage_vector = embed_passage("퍼팅은 어깨로 만드는 진자 스트로크가 중요하다")

    assert len(query_vector) == EMBEDDING_DIM
    assert len(passage_vector) == EMBEDDING_DIM
    assert EMBEDDING_MODEL_NAME  # 모델명이 비어있지 않은지만 확인


def test_search_similar_returns_most_relevant_entry_first():
    suffix = uuid.uuid4().hex[:8]
    putting_title = f"테스트-퍼팅거리감-{suffix}"
    ob_title = f"테스트-OB규칙-{suffix}"

    _seed_knowledge(
        "putting",
        putting_title,
        "3퍼팅을 줄이려면 롱퍼팅 거리감 연습이 중요하다. 여러 거리에서 홀 주변에 볼을 세우는 훈련을 한다.",
    )
    _seed_knowledge(
        "rule",
        ob_title,
        "볼이 OB 구역으로 나가면 1벌타 후 원래 자리에서 다시 쳐야 한다.",
    )

    # top_k를 넉넉하게 잡아 사전 시드된 골프 지식(knowledge_data.py)까지 모두 포함시킨 뒤,
    # 두 테스트 항목 사이의 "상대 순위"만 검증한다 — top_k=1로 전역 최상위만 보면 사전 시드된
    # 다른 항목(예: "3퍼팅을 줄이는 거리감 연습")이 더 가깝게 나와 테스트가 불안정해진다.
    db = SessionLocal()
    try:
        results = retrieve_knowledge(
            db, "3퍼팅이 너무 많이 나와요 거리감을 어떻게 연습해야 하나요", top_k=100
        )
    finally:
        db.close()

    titles = [entry.title for entry in results]
    assert titles.index(putting_title) < titles.index(ob_title)


def test_retrieve_knowledge_returns_empty_list_for_blank_query():
    db = SessionLocal()
    try:
        results = retrieve_knowledge(db, "   ")
    finally:
        db.close()

    assert results == []
