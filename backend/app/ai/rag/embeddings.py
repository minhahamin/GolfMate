"""RAG용 임베딩 모델 초기화.

OpenRouter는 임베딩 API를 제공하지 않고, 별도 유료 임베딩 API를 새로 붙이면 지금까지
지켜온 "무료 LLM만 사용" 원칙이 깨진다. 대신 로컬에서 실행되는 sentence-transformers
(intfloat/multilingual-e5-small, 한국어 지원, 384차원)를 API 키 없이 그대로 쓴다.

e5 계열 모델은 검색 성능을 위해 입력 앞에 "query: "/"passage: " 접두사를 붙이는 것이
공식 컨벤션이다 (질문 임베딩과 문서 임베딩을 구분).
"""
from functools import lru_cache

from sentence_transformers import SentenceTransformer

EMBEDDING_MODEL_NAME = "intfloat/multilingual-e5-small"


@lru_cache
def get_embedding_model() -> SentenceTransformer:
    return SentenceTransformer(EMBEDDING_MODEL_NAME)


def embed_query(text: str) -> list[float]:
    model = get_embedding_model()
    return model.encode(f"query: {text}", normalize_embeddings=True).tolist()


def embed_passage(text: str) -> list[float]:
    model = get_embedding_model()
    return model.encode(f"passage: {text}", normalize_embeddings=True).tolist()


def embed_passages(texts: list[str]) -> list[list[float]]:
    model = get_embedding_model()
    vectors = model.encode([f"passage: {text}" for text in texts], normalize_embeddings=True)
    return vectors.tolist()
