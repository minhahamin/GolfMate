"""LLM 응답을 6개 섹션으로 파싱 (Coach의 app/ai/coach/parser.py와 동일한 설계).

모델을 교체해도 안정적으로 동작하도록 JSON/함수호출 대신 단순 텍스트 헤더 파싱을 쓴다.
헤더를 못 찾으면 원문 전체를 summary에 담아 최소한 화면에 뭔가는 보이도록 한다.
"""
import re

SECTION_KEYS = [
    ("mood", "기분"),
    ("highlights", "하이라이트"),
    ("improvement_points", "개선점"),
    ("next_goal", "다음목표"),
    ("summary", "요약"),
]

MATCHED_ROUND_LABEL = "매칭라운드"


def parse_diary_response(text: str) -> dict[str, str | int | None]:
    all_labels = [label for _, label in SECTION_KEYS] + [MATCHED_ROUND_LABEL]
    pattern = "|".join(re.escape(label) for label in all_labels)
    splits = re.split(rf"\[({pattern})\]", text)

    if len(splits) < 3:
        return {key: "" for key, _ in SECTION_KEYS} | {"summary": text.strip(), "matched_round_id": None}

    label_to_key = {label: key for key, label in SECTION_KEYS}
    result: dict[str, str] = {key: "" for key, _ in SECTION_KEYS}
    matched_round_raw = ""

    # splits: [머리말, 라벨1, 내용1, 라벨2, 내용2, ...]
    for i in range(1, len(splits), 2):
        label = splits[i]
        content = splits[i + 1].strip() if i + 1 < len(splits) else ""
        if label == MATCHED_ROUND_LABEL:
            matched_round_raw = content
            continue
        key = label_to_key.get(label)
        if key:
            result[key] = content

    result["matched_round_id"] = _parse_matched_round_id(matched_round_raw)
    return result


def _parse_matched_round_id(raw: str) -> int | None:
    match = re.search(r"\d+", raw)
    return int(match.group()) if match else None
