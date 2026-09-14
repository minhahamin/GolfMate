"""데모 계정 시드 스크립트.

포트폴리오 방문자가 회원가입 없이 바로 체험할 수 있도록, 그럴듯한 라운드 기록이 채워진
데모 계정을 만든다. 이미 있으면 건너뛴다 (여러 번 실행해도 안전).

실행:
    docker compose exec backend python -m app.seed_demo_account
"""
import random
from datetime import date, timedelta

from app.core.database import SessionLocal
from app.core.security import hash_password
from app.repositories import course_repository, golfer_profile_repository, round_repository, user_repository

DEMO_EMAIL = "demo@golfmate.ai"
DEMO_PASSWORD = "golfmate-demo!"
DEMO_NAME = "김도현"

# 최근 순으로 정렬해서 만들 라운드들: (며칠 전, 목표 스코어)
DEMO_ROUNDS = [
    (70, 98),
    (60, 96),
    (49, 94),
    (38, 93),
    (28, 90),
    (19, 89),
    (11, 87),
    (4, 85),
]

_rng = random.Random(42)  # 매번 같은 데이터가 나오도록 시드 고정


def _generate_holes(course_holes: list, target_score: int) -> list[dict]:
    """course_holes(파 구성)에 맞춰 target_score에 합이 맞는 그럴듯한 홀 기록을 만든다."""
    pars = [ch.par for ch in course_holes]
    total_par = sum(pars)
    extra = target_score - total_par  # 전체적으로 더 쳐야 하는 타수

    scores = list(pars)
    # extra만큼 무작위 홀에 1타씩 분배 (음수면 반대로 버디 부여)
    step = 1 if extra >= 0 else -1
    for _ in range(abs(extra)):
        idx = _rng.randrange(len(scores))
        scores[idx] += step

    holes = []
    for course_hole, score in zip(course_holes, scores):
        par = course_hole.par
        diff = score - par
        putts = 2 if diff <= 0 else _rng.choice([2, 2, 3])
        fairway_hit = par != 3 and _rng.random() < 0.55
        gir = diff <= 0 and _rng.random() < 0.7
        holes.append(
            {
                "hole_number": course_hole.hole_number,
                "par": par,
                "score": max(score, 1),
                "putts": putts,
                "fairway_hit": fairway_hit,
                "gir": gir,
                "ob": 1 if diff >= 3 and _rng.random() < 0.3 else 0,
                "bunker": 1 if _rng.random() < 0.15 else 0,
                "penalty": 1 if diff >= 2 and _rng.random() < 0.2 else 0,
            }
        )
    return holes


def run() -> None:
    db = SessionLocal()
    try:
        if user_repository.get_by_email(db, DEMO_EMAIL) is not None:
            print("데모 계정이 이미 있어 건너뜁니다.")
            return

        courses = course_repository.list_all(db)
        if not courses:
            print("코스가 없어 데모 계정을 만들 수 없습니다. seed_courses를 먼저 실행하세요.")
            return

        user = user_repository.create(
            db, email=DEMO_EMAIL, hashed_password=hash_password(DEMO_PASSWORD), name=DEMO_NAME
        )
        golfer_profile_repository.create_empty(db, user_id=user.id)
        db.flush()

        profile = golfer_profile_repository.get_by_user_id(db, user.id)
        golfer_profile_repository.update(
            db,
            profile,
            {
                "handicap": 16.4,
                "average_score": 91.5,
                "driver_distance": 210,
                "iron_distance": 150,
                "putting_average": 32.0,
                "fairway_percentage": 52.0,
                "gir_percentage": 38.0,
                "preferred_tee": "레귤러",
                "goal_score": 85,
            },
        )

        for i, (days_ago, target_score) in enumerate(DEMO_ROUNDS):
            course = courses[i % len(courses)]
            course_detail = course_repository.get_by_id(db, course.id)
            holes = _generate_holes(course_detail.holes, target_score)
            actual_score = sum(h["score"] for h in holes)

            round_ = round_repository.create(
                db,
                user_id=user.id,
                course_id=course.id,
                round_date=date.today() - timedelta(days=days_ago),
                score=actual_score,
                weather=_rng.choice(["맑음", "흐림", "약한 바람"]),
                temperature=round(_rng.uniform(15, 27), 1),
                wind=_rng.choice(["약함", "보통", "강함"]),
                memo=None,
            )
            round_repository.replace_holes(db, round_.id, holes)

        db.commit()
        print(f"데모 계정 생성됨: {DEMO_EMAIL} / 라운드 {len(DEMO_ROUNDS)}개")
    finally:
        db.close()


if __name__ == "__main__":
    run()
