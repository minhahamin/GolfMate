"""LLM 응답을 5개 섹션으로 파싱.

모델을 교체해도(예: OpenRouter 무료 모델 변경) 안정적으로 동작하도록 JSON/함수호출
대신 단순 텍스트 헤더 파싱을 쓴다. 헤더를 못 찾으면 원문 전체를 current_state에 담아
최소한 화면에 뭔가는 보이도록 한다.
"""
import re

SECTION_KEYS = [
    ("current_state", "현재 상태"),
    ("biggest_problem", "가장 큰 문제"),
    ("cause", "문제의 원인"),
    ("strategy", "추천 전략"),
    ("next_goal", "다음 라운드 목표"),
]


def parse_coach_response(text: str) -> dict[str, str]:
    pattern = "|".join(re.escape(label) for _, label in SECTION_KEYS)
    splits = re.split(rf"\[({pattern})\]", text)

    if len(splits) < 3:
        # 헤더를 못 찾음 — 원문을 그대로 current_state에 넣어 최소한의 응답은 보장한다.
        return {key: "" for key, _ in SECTION_KEYS} | {"current_state": text.strip()}

    label_to_key = {label: key for key, label in SECTION_KEYS}
    result = {key: "" for key, _ in SECTION_KEYS}

    # splits: [머리말, 라벨1, 내용1, 라벨2, 내용2, ...]
    for i in range(1, len(splits), 2):
        label = splits[i]
        content = splits[i + 1].strip() if i + 1 < len(splits) else ""
        key = label_to_key.get(label)
        if key:
            result[key] = content

    return result
