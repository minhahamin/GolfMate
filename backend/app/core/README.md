# core/

애플리케이션 전역 인프라 코드.

- `config.py` — `pydantic-settings`로 환경변수를 로드하는 `Settings` 클래스.
  API Key, DB 접속 정보 등은 절대 코드에 하드코딩하지 않고 여기서만 읽는다.
- `database.py` — SQLAlchemy `engine`, `SessionLocal`, FastAPI 의존성 `get_db()`.
  DB 연결과 관련된 코드는 이 파일에만 두고 다른 곳에서 `create_engine`을 다시 호출하지 않는다.

Phase 2에서 JWT 발급/검증을 담당할 `security.py`가 이 폴더에 추가될 예정이다.
