"""Mock 골프장 시드 스크립트.

실제 골프장 API 연동 전까지 사용할 가상의 코스 데이터를 넣는다.
이미 같은 이름의 코스가 있으면 건너뛴다 (여러 번 실행해도 안전).

Phase 7부터 difficulty/green_fee_avg/tags를 채워, course_repository.search가 이 값으로
후보를 필터링하고 AI가 그 후보 중에서만 추천하도록 한다 (app/ai/recommend/graph.py 참고).

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
        "difficulty": "초급",
        "green_fee_avg": 110000,
        "tags": "구릉지,초보자추천,넓은페어웨이",
    },
    {
        "name": "선셋베이 골프리조트",
        "region": "제주도 서귀포",
        "address": "제주특별자치도 서귀포시 (가상 주소)",
        "description": "바다를 끼고 도는 링크스 스타일 코스. 바람의 영향이 커 전략적인 클럽 선택이 중요하다.",
        "distance_offset": 15,
        "difficulty": "고급",
        "green_fee_avg": 230000,
        "tags": "바다전망,링크스,바람강함",
    },
    {
        "name": "파인밸리 골프클럽",
        "region": "강원도 춘천",
        "address": "강원도 춘천시 (가상 주소)",
        "description": "소나무 숲으로 둘러싸인 산악 코스. 고저차가 커 거리 계산이 까다롭다.",
        "distance_offset": 5,
        "difficulty": "고급",
        "green_fee_avg": 150000,
        "tags": "산악,소나무숲,고저차큼",
    },
    {
        "name": "레이크사이드 컨트리클럽",
        "region": "경기도 용인",
        "address": "경기도 용인시 기흥구 (가상 주소)",
        "description": "호수를 낀 평탄한 코스로 워터해저드가 많아 정확한 아이언샷이 필요하다.",
        "distance_offset": -5,
        "difficulty": "중급",
        "green_fee_avg": 140000,
        "tags": "호수전망,워터해저드,평탄한코스",
    },
    {
        "name": "오션뷰 골프앤리조트",
        "region": "부산 기장군",
        "address": "부산광역시 기장군 (가상 주소)",
        "description": "해안 절벽을 따라 이어지는 코스로 대부분의 홀에서 바다가 보인다.",
        "distance_offset": 10,
        "difficulty": "고급",
        "green_fee_avg": 210000,
        "tags": "바다전망,해안절벽,포토스팟",
    },
    {
        "name": "선샤인힐스 컨트리클럽",
        "region": "충청북도 청주",
        "address": "충청북도 청주시 (가상 주소)",
        "description": "완만한 구릉과 넓은 그린으로 초보자가 편하게 라운드하기 좋다.",
        "distance_offset": -15,
        "difficulty": "초급",
        "green_fee_avg": 95000,
        "tags": "초보자추천,넓은그린,가성비",
    },
    {
        "name": "베이사이드 골프클럽",
        "region": "인천 영종도",
        "address": "인천광역시 중구 영종도 (가상 주소)",
        "description": "공항 인근 평지 코스. 바람이 적어 스코어 관리에 유리하다.",
        "distance_offset": -8,
        "difficulty": "중급",
        "green_fee_avg": 120000,
        "tags": "평지,공항인근,바람적음",
    },
    {
        "name": "스카이릿지 컨트리클럽",
        "region": "경상북도 경주",
        "address": "경상북도 경주시 (가상 주소)",
        "description": "능선을 따라 조성된 고지대 코스로 조망이 뛰어나지만 체력 소모가 크다.",
        "distance_offset": 8,
        "difficulty": "고급",
        "green_fee_avg": 160000,
        "tags": "고지대,능선코스,조망우수",
    },
    {
        "name": "가든밸리 컨트리클럽",
        "region": "전라남도 순천",
        "address": "전라남도 순천시 (가상 주소)",
        "description": "정원처럼 조경이 잘 가꾸어진 평지 코스. 가족 단위 초보자에게 인기가 많다.",
        "distance_offset": -12,
        "difficulty": "초급",
        "green_fee_avg": 100000,
        "tags": "조경우수,가족친화,평지",
    },
    {
        "name": "리버사이드 골프클럽",
        "region": "경기도 여주",
        "address": "경기도 여주시 (가상 주소)",
        "description": "강을 따라 조성된 코스로 여러 홀에서 강을 가로지르는 티샷이 요구된다.",
        "distance_offset": 3,
        "difficulty": "중급",
        "green_fee_avg": 130000,
        "tags": "강전망,전략적티샷,중급자추천",
    },
]


def run() -> None:
    db = SessionLocal()
    try:
        for course_data in MOCK_COURSES:
            existing = db.query(Course).filter(Course.name == course_data["name"]).first()
            if existing is not None:
                # Phase 7 이전에 만들어진 코스는 difficulty/green_fee_avg/tags가 비어있을 수
                # 있어, 새 필드만 멱등적으로 채워 넣는다 (기존 라운드 데이터를 건드리지 않음).
                existing.difficulty = course_data["difficulty"]
                existing.green_fee_avg = course_data["green_fee_avg"]
                existing.tags = course_data["tags"]
                print(f"이미 존재함, 추천 필드만 갱신: {course_data['name']}")
                continue

            course = Course(
                name=course_data["name"],
                region=course_data["region"],
                address=course_data["address"],
                description=course_data["description"],
                holes_count=18,
                par=sum(HOLE_PARS),
                difficulty=course_data["difficulty"],
                green_fee_avg=course_data["green_fee_avg"],
                tags=course_data["tags"],
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
