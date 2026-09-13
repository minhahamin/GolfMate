"""헬스체크 엔드포인트 스모크 테스트.

DB 접속이 필요한 /api/health/db는 실제 DB가 떠 있는 통합 테스트 환경에서만
의미가 있으므로, 여기서는 DB 없이도 항상 통과하는 /api/health만 검증한다.
"""
from fastapi.testclient import TestClient

from app.main import app

client = TestClient(app)


def test_liveness_check_returns_ok():
    response = client.get("/api/health")

    assert response.status_code == 200
    assert response.json() == {"status": "ok"}
