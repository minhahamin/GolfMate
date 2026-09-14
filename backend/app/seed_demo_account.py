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
from app.repositories import (
    course_repository,
    diary_repository,
    golfer_profile_repository,
    round_repository,
    user_repository,
)

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

# Phase 6 AI 골프 일기 데모 데이터. 컨테이너 부팅 시 LLM(OpenRouter) 호출 없이도 데모
# 방문자가 바로 결과물을 볼 수 있도록, AI 파이프라인을 거치지 않고 완성된 텍스트를 직접
# 심는다 (seed_courses/seed_golf_knowledge와 마찬가지로 네트워크 의존 없는 멱등 시드).
DEMO_DIARIES = [
    {
        "raw_text": (
            "오늘 라운드는 전반에 드라이버가 잘 맞아서 기분 좋게 시작했는데, "
            "후반 들어 퍼팅이 계속 짧게 가서 3퍼팅이 많았다. 그래도 마지막 홀에서 "
            "파를 잡아서 나쁘지 않게 마무리했다."
        ),
        "summary": "전반 드라이버 샷감이 좋았지만 후반 3퍼팅이 반복돼 스코어를 지켰다.",
        "mood": "아쉽지만 만족",
        "highlights": "전반 드라이버 샷감, 마지막 홀 파 마무리",
        "improvement_points": "후반 퍼팅 거리감 — 짧은 퍼팅이 계속 모자랐다",
        "next_goal": "다음 라운드에서는 그린 주변 퍼팅 거리감 연습 후 라운드에 임하기",
    },
    {
        "raw_text": (
            "비가 살짝 와서 그립이 미끄러웠는데도 페어웨이 적중률이 평소보다 높았다. "
            "다만 벙커에 두 번이나 빠져서 거기서 타수를 많이 잃었다. "
            "전체적으로는 평소보다 나은 라운드였다."
        ),
        "summary": "궂은 날씨에도 페어웨이 적중률이 좋았지만 벙커샷에서 타수를 잃었다.",
        "mood": "만족",
        "highlights": "평소보다 높은 페어웨이 적중률",
        "improvement_points": "벙커샷 — 두 번 모두 탈출에 실패해 타수 손실",
        "next_goal": "벙커샷 연습을 다음 연습 라운드에 포함하기",
    },
]


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


def _seed_demo_diaries(db, user_id: int) -> None:
    """멱등적으로 데모 일기를 심는다 — 이미 일기가 있으면 건너뛴다."""
    if diary_repository.list_by_user(db, user_id):
        print("데모 일기가 이미 있어 건너뜁니다.")
        return

    recent_rounds = round_repository.list_recent_by_user(db, user_id, limit=len(DEMO_DIARIES))
    if not recent_rounds:
        print("데모 라운드가 없어 데모 일기를 만들 수 없습니다.")
        return

    for diary_data, round_ in zip(DEMO_DIARIES, recent_rounds):
        diary_repository.create(db, user_id=user_id, round_id=round_.id, **diary_data)
    db.commit()
    print(f"데모 일기 생성됨: {len(DEMO_DIARIES)}개")


def run() -> None:
    db = SessionLocal()
    try:
        existing_user = user_repository.get_by_email(db, DEMO_EMAIL)
        if existing_user is not None:
            print("데모 계정이 이미 있어 라운드 시드는 건너뜁니다.")
            _seed_demo_diaries(db, existing_user.id)
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

        _seed_demo_diaries(db, user.id)
    finally:
        db.close()


if __name__ == "__main__":
    run()
