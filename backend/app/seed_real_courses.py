"""실제 골프장 시드 스크립트 — 문화체육관광부 「전국 골프장 현황」(2024-12-31 기준) CSV.

data/golf_courses_kr.csv에서 읽는다 (공공데이터포털 파일데이터, 네트워크 불필요).
같은 이름+주소의 행은 18홀+9홀처럼 코스가 나뉘어 있는 경우라 홀 수를 합쳐 하나로 만든다.
이미 있는 코스는 건너뛰므로 여러 번 실행해도 안전하다.

공공데이터에 없는 값(난이도, 그린피, 좌표, 홀별 파/거리)은 NULL로 둔다 — 가짜 값을 채우지 않는다.

실행:
    docker compose exec backend python -m app.seed_real_courses
"""
import csv
from collections import OrderedDict
from pathlib import Path

from app.core.database import SessionLocal
from app.models.course import Course

CSV_PATH = Path(__file__).resolve().parent.parent / "data" / "golf_courses_kr.csv"
SOURCE_NOTE = "출처: 문화체육관광부 전국 골프장 현황(2024-12-31)"


def _full_address(sido_full: str, sido_abbr: str, raw: str) -> str:
    raw = raw.strip()
    if raw.startswith(sido_full):
        return raw
    if raw.startswith(sido_abbr + " "):
        return f"{sido_full} {raw[len(sido_abbr) + 1:]}"
    return f"{sido_full} {raw}"


def load_courses() -> list[dict]:
    merged: "OrderedDict[tuple[str, str], dict]" = OrderedDict()
    with open(CSV_PATH, encoding="utf-8-sig", newline="") as f:
        for row in csv.DictReader(f):
            name = row["이름"].strip()
            sido_full = row["행정구역_시도명(현행)"].strip()
            address = _full_address(sido_full, row["지역"].strip(), row["소재지"])
            sigungu = row["행정구역_시군구명"].strip() or address.split()[1]
            key = (name, address)
            holes = int(row["홀"])
            if key in merged:
                merged[key]["holes_count"] += holes
                continue
            merged[key] = {
                "name": name,
                "region": f"{sido_full} {sigungu}",
                "address": address,
                "holes_count": holes,
                "category": row["구분"].strip(),
            }
    return list(merged.values())


def run() -> None:
    courses = load_courses()
    db = SessionLocal()
    try:
        existing = {(c.name, c.address) for c in db.query(Course).filter(Course.is_demo.is_(False))}
        created = 0
        for data in courses:
            if (data["name"], data["address"]) in existing:
                continue
            holes = data["holes_count"]
            db.add(
                Course(
                    name=data["name"],
                    region=data["region"],
                    address=data["address"],
                    description=f"{data['category']} 골프장, 총 {holes}홀. {SOURCE_NOTE}",
                    holes_count=holes,
                    # 공공데이터에 파 정보가 없다 — 18홀 기준 표준 파(홀당 4)로 근사한다.
                    par=4 * min(holes, 18),
                    difficulty=None,
                    green_fee_avg=None,
                    tags=data["category"],
                    is_demo=False,
                )
            )
            created += 1
        db.commit()
        print(f"실제 골프장 {created}곳 추가 (CSV {len(courses)}곳, 기존 {len(existing)}곳)")
    finally:
        db.close()


if __name__ == "__main__":
    run()
