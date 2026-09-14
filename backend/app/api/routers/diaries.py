"""AI 골프 일기 CRUD 엔드포인트. 모두 로그인이 필요하고, 본인 일기만 다룬다.

생성은 JSON이 아니라 multipart/form-data다 — 텍스트 또는 오디오 파일 중 하나 이상을
받는다(둘 다 없으면 400, 오디오 전사에 실패하면 422).
"""
from fastapi import APIRouter, Depends, File, Form, UploadFile
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.security import get_current_user
from app.models.user import User
from app.schemas.diary import DiaryListItem, DiaryRead
from app.services import diary_service

router = APIRouter(prefix="/diaries", tags=["diaries"])


@router.get("", response_model=list[DiaryListItem])
def list_diaries(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> list[DiaryListItem]:
    return diary_service.list_my_diaries(db, current_user.id)


@router.post("", response_model=DiaryRead, status_code=201)
def create_diary(
    text: str | None = Form(default=None, max_length=2000),
    round_id: int | None = Form(default=None),
    audio: UploadFile | None = File(default=None),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> DiaryRead:
    audio_bytes = audio.file.read() if audio is not None else None
    diary = diary_service.create_diary(
        db,
        current_user.id,
        text=text,
        audio_bytes=audio_bytes,
        audio_filename=audio.filename if audio is not None else None,
        round_id_hint=round_id,
    )
    return DiaryRead(**diary_service.to_read_dict(diary))


@router.get("/{diary_id}", response_model=DiaryRead)
def get_diary(
    diary_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> DiaryRead:
    diary = diary_service.get_my_diary(db, current_user.id, diary_id)
    return DiaryRead(**diary_service.to_read_dict(diary))


@router.delete("/{diary_id}", status_code=204)
def delete_diary(
    diary_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> None:
    diary_service.delete_my_diary(db, current_user.id, diary_id)
