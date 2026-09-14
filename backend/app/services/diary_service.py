"""AI 골프 일기 생성/조회/삭제 비즈니스 로직.

Round와 마찬가지로 모든 조회/삭제는 반드시 user_id로 소유권을 확인한다 — 다른 사용자의
일기는 존재 자체를 알 수 없도록 404로만 응답한다 (403이 아니다).
"""
from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from app.ai.diary.graph import run_diary_graph
from app.ai.stt.transcriber import SttTranscriptionError, transcribe_audio
from app.models.diary import Diary
from app.repositories import diary_repository, round_repository

NOT_FOUND = HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="일기를 찾을 수 없습니다.")


def _round_summary(diary: Diary) -> str | None:
    round_ = diary.round
    if round_ is None:
        return None
    course_name = round_.course.name if round_.course else "코스 미상"
    return f"{round_.round_date} {course_name} · {round_.score}타"


def to_read_dict(diary: Diary) -> dict:
    return {
        "id": diary.id,
        "round_id": diary.round_id,
        "round_summary": _round_summary(diary),
        "raw_text": diary.raw_text,
        "summary": diary.summary,
        "mood": diary.mood,
        "highlights": diary.highlights,
        "improvement_points": diary.improvement_points,
        "next_goal": diary.next_goal,
        "created_at": diary.created_at,
    }


def create_diary(
    db: Session,
    user_id: int,
    *,
    text: str | None,
    audio_bytes: bytes | None,
    audio_filename: str | None,
    round_id_hint: int | None,
) -> Diary:
    if audio_bytes:
        try:
            raw_text = transcribe_audio(audio_bytes, audio_filename)
        except SttTranscriptionError as exc:
            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                detail="음성을 인식하지 못했습니다. 다시 녹음해주세요.",
            ) from exc
    else:
        raw_text = (text or "").strip()

    if not raw_text:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="일기 내용을 입력하거나 음성을 녹음해주세요.",
        )

    if round_id_hint is not None and round_repository.get_by_id_for_user(db, round_id_hint, user_id) is None:
        raise NOT_FOUND

    result = run_diary_graph(db, user_id, raw_text, round_id_hint)

    diary = diary_repository.create(
        db,
        user_id=user_id,
        round_id=result["matched_round_id"],
        raw_text=raw_text,
        summary=result["summary"],
        mood=result["mood"],
        highlights=result["highlights"],
        improvement_points=result["improvement_points"],
        next_goal=result["next_goal"],
    )
    db.commit()
    return diary_repository.get_by_id_for_user(db, diary.id, user_id)


def list_my_diaries(db: Session, user_id: int) -> list[Diary]:
    return diary_repository.list_by_user(db, user_id)


def get_my_diary(db: Session, user_id: int, diary_id: int) -> Diary:
    diary = diary_repository.get_by_id_for_user(db, diary_id, user_id)
    if diary is None:
        raise NOT_FOUND
    return diary


def delete_my_diary(db: Session, user_id: int, diary_id: int) -> None:
    diary = get_my_diary(db, user_id, diary_id)
    diary_repository.delete(db, diary)
    db.commit()
