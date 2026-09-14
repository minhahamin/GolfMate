"""LLM 응답을 3개 섹션(홀공략/위험요소/클럽전략)으로 파싱.

Coach/Diary와 동일한 설계(모델 교체에도 안정적인 헤더 기반 텍스트 파싱).
"""
import re

SECTION_KEYS = [
    ("hole_analysis", "홀공략"),
    ("risk_analysis", "위험요소"),
    ("club_strategy", "클럽전략"),
]


def parse_caddie_response(text: str) -> dict[str, str]:
    pattern = "|".join(re.escape(label) for _, label in SECTION_KEYS)
    splits = re.split(rf"\[({pattern})\]", text)

    if len(splits) < 3:
        return {key: "" for key, _ in SECTION_KEYS} | {"hole_analysis": text.strip()}

    label_to_key = {label: key for key, label in SECTION_KEYS}
    result = {key: "" for key, _ in SECTION_KEYS}

    for i in range(1, len(splits), 2):
        label = splits[i]
        content = splits[i + 1].strip() if i + 1 < len(splits) else ""
        key = label_to_key.get(label)
        if key:
            result[key] = content

    return result
