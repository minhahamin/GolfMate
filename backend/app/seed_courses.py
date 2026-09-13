"""Mock 골프장 시드 스크립트.

실제 골프장 API 연동(Phase 7) 전까지 사용할 가상의 코스 데이터를 넣는다.
이미 같은 이름의 코스가 있으면 건너뛴다 (여러 번 실행해도 안전).

실행:
    docker compose exec backend python -m app.seed_courses
"""
from app.core.database import SessionLocal
from app.models.course import Course
from app.models.course_hole import CourseHole

# 18홀 파 구성: 파3 4개, 파4 10개, 파5 4개 (합계 파72) — 일반적인 챔피언십 코스 구성.
HOLE_PARS = [4, 4, 3, 5, 4, 4, 3, 4, 5, 4, 3, 4, 5, 4, 4, 3, 4, 5]

DISTANCE_BY_PAR = {3: 165, 4: 360, 5: 500}

MOCK_COURSES = [
    {
        "name": "그린힐 컨트리클럽",
        "region": "경기도 용인",
        "address": "경기도 용인시 처인구 (가상 주소)",
        "description": "완만한 구릉지에 자리한 27홀 규모의 컨트리클럽. 페어웨이가 넓어 초중급자에게 적합하다.",
        "distance_offset": -10,
    },
    {
        "name": "선셋베이 골프리조트",
        "region": "제주도 서귀포",
        "address": "제주특별자치도 서귀포시 (가상 주소)",
        "description": "바다를 끼고 도는 링크스 스타일 코스. 바람의 영향이 커 전략적인 클럽 선택이 중요하다.",
        "distance_offset": 15,
    },
    {
        "name": "파인밸리 골프클럽",
        "region": "강원도 춘천",
        "address": "강원도 춘천시 (가상 주소)",
        "description": "소나무 숲으로 둘러싸인 산악 코스. 고저차가 커 거리 계산이 까다롭다.",
        "distance_offset": 5,
    },
]


def run() -> None:
    db = SessionLocal()
    try:
        for course_data in MOCK_COURSES:
            existing = db.query(Course).filter(Course.name == course_data["name"]).first()
            if existing is not None:
                print(f"이미 존재함, 건너뜀: {course_data['name']}")
                continue

            course = Course(
                name=course_data["name"],
                region=course_data["region"],
                address=course_data["address"],
                description=course_data["description"],
                holes_count=18,
                par=sum(HOLE_PARS),
            )
            db.add(course)
            db.flush()

            offset = course_data["distance_offset"]
            for hole_number, par in enumerate(HOLE_PARS, start=1):
                db.add(
                    CourseHole(
                        course_id=course.id,
                        hole_number=hole_number,
                        par=par,
                        distance_meters=DISTANCE_BY_PAR[par] + offset,
                    )
                )

            print(f"생성됨: {course_data['name']} (파{course.par}, 18홀)")

        db.commit()
    finally:
        db.close()


if __name__ == "__main__":
    run()
