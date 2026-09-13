# core/

애플리케이션 전역 인프라 코드.

- `config.py` — `pydantic-settings`로 환경변수를 로드하는 `Settings` 클래스.
  API Key, DB 접속 정보 등은 절대 코드에 하드코딩하지 않고 여기서만 읽는다.
- `database.py` — SQLAlchemy `engine`, `SessionLocal`, FastAPI 의존성 `get_db()`.
  DB 연결과 관련된 코드는 이 파일에만 두고 다른 곳에서 `create_engine`을 다시 호출하지 않는다.
- `security.py` — 비밀번호 해싱(`bcrypt`), JWT 발급/검증(`pyjwt`), 그리고 보호된 엔드포인트가
  쓰는 `get_current_user` 의존성. `Authorization: Bearer <token>` 헤더를 여기서만 파싱한다.
