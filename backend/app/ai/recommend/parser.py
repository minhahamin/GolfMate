"""LLM 응답을 순위별 추천 목록으로 파싱.

Coach/Diary의 헤더 기반 파싱과 같은 이유(모델 교체에도 안정적으로 동작)로 JSON/함수호출
대신 텍스트 헤더를 쓴다. [총평]과 1~3위 각각의 id/이유 블록을 파싱한다.
"""
import re

RANK_HEADER_PATTERN = re.compile(r"\[(\d)위\]")
SUMMARY_HEADER = "[총평]"


def parse_recommend_response(text: str) -> dict:
    summary = ""
    summary_match = re.search(rf"{re.escape(SUMMARY_HEADER)}\s*(.*?)(?=\[\d위\]|\Z)", text, re.DOTALL)
    if summary_match:
        summary = summary_match.group(1).strip()

    ranked: list[dict] = []
    blocks = RANK_HEADER_PATTERN.split(text)
    # blocks: [머리말/총평, 순위숫자1, 내용1, 순위숫자2, 내용2, ...]
    for i in range(1, len(blocks), 2):
        content = blocks[i + 1] if i + 1 < len(blocks) else ""
        id_match = re.search(r"id\s*[:：]\s*(\d+)", content)
        reason_match = re.search(r"이유\s*[:：]\s*(.+)", content, re.DOTALL)
        if not id_match:
            continue
        reason = reason_match.group(1).strip() if reason_match else ""
        # 다음 헤더 전까지만 이유로 취급 (혹시 남아있을 후행 공백/개행 정리)
        reason = reason.split("\n\n")[0].strip()
        ranked.append({"course_id": int(id_match.group(1)), "reason": reason})

    return {"summary": summary, "ranked": ranked}
