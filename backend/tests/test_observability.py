"""Langfuse observability(Phase 10) 단위 테스트 — DB/네트워크 없이 순수하게 검증한다.

LANGFUSE_PUBLIC_KEY/SECRET_KEY를 설정하지 않은 채(테스트 환경 기본값) 핸들러를 만들어도
예외 없이 no-op으로 동작해야 한다는, "관측 기능이 꺼져 있어도 AI 기능엔 영향이 없다"는
설계 전제를 검증한다.
"""
from app.ai.llm.observability import build_langfuse_config, get_langfuse_handler


def test_get_langfuse_handler_does_not_raise_without_keys():
    handler = get_langfuse_handler()

    assert handler is not None
    # 같은 프로세스에서는 항상 같은 싱글턴 핸들러를 재사용한다 (lru_cache).
    assert get_langfuse_handler() is handler


def test_build_langfuse_config_tags_trace_by_graph_and_user():
    config = build_langfuse_config("coach", user_id=42)

    assert config["callbacks"] == [get_langfuse_handler()]
    assert config["metadata"]["langfuse_trace_name"] == "coach_graph"
    assert config["metadata"]["langfuse_user_id"] == "42"
    assert config["metadata"]["langfuse_tags"] == ["coach"]
