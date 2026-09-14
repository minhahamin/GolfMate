FROM python:3.12-slim

WORKDIR /app

# psycopg2-binary 빌드에 필요한 최소 시스템 패키지
RUN apt-get update \
    && apt-get install -y --no-install-recommends libpq-dev gcc \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

EXPOSE 8000

# 컨테이너가 뜰 때마다 마이그레이션과 코스/데모계정 시드를 먼저 실행한다 (모두 멱등적이라
# 이미 최신 상태여도 안전하다). 로컬 개발과 Railway 배포가 같은 절차를 따르게 되어
# "원격 DB에 마이그레이션을 어떻게 적용하나" 문제를 별도 설정 없이 해결한다.
CMD ["sh", "-c", "alembic upgrade head && python -m app.seed_courses && python -m app.seed_demo_account && python -m app.seed_golf_knowledge && uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload"]
