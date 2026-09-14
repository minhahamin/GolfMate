"""그룹 CRUD + 멤버 관리 비즈니스 로직.

모든 조회는 반드시 멤버십을 확인한다 — 멤버가 아닌 그룹은 존재 자체를 알 수 없도록 404로만
응답한다 (403이 아니다, round_service.py와 동일한 원칙).
"""
from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from app.models.group import Group
from app.repositories import group_repository, user_repository

NOT_FOUND = HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="그룹을 찾을 수 없습니다.")


def to_detail_dict(group: Group) -> dict:
    return {
        "id": group.id,
        "name": group.name,
        "owner_id": group.owner_id,
        "created_at": group.created_at,
        "members": [
            {"user_id": m.user_id, "name": m.user.name, "email": m.user.email, "joined_at": m.joined_at}
            for m in group.members
        ],
    }


def create_group(db: Session, owner_id: int, name: str) -> Group:
    group = group_repository.create(db, name=name, owner_id=owner_id)
    db.commit()
    return group_repository.get_by_id_for_member(db, group.id, owner_id)


def list_my_groups(db: Session, user_id: int) -> list[Group]:
    return group_repository.list_by_user(db, user_id)


def get_group_detail(db: Session, group_id: int, user_id: int) -> Group:
    group = group_repository.get_by_id_for_member(db, group_id, user_id)
    if group is None:
        raise NOT_FOUND
    return group


def add_member_by_email(db: Session, group_id: int, requester_id: int, email: str) -> Group:
    group = get_group_detail(db, group_id, requester_id)
    if group.owner_id != requester_id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="그룹장만 멤버를 추가할 수 있습니다.")

    new_member = user_repository.get_by_email(db, email)
    if new_member is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="해당 이메일의 사용자를 찾을 수 없습니다.")

    if any(m.user_id == new_member.id for m in group.members):
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="이미 그룹에 속한 사용자입니다.")

    group_repository.add_member(db, group_id, new_member.id)
    db.commit()
    return group_repository.get_by_id_for_member(db, group_id, requester_id)


def remove_member(db: Session, group_id: int, requester_id: int, target_user_id: int) -> None:
    group = get_group_detail(db, group_id, requester_id)
    if requester_id != target_user_id and group.owner_id != requester_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN, detail="본인 탈퇴이거나 그룹장만 멤버를 제거할 수 있습니다."
        )
    if target_user_id == group.owner_id:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="그룹장은 그룹을 나갈 수 없습니다.")

    group_repository.remove_member(db, group_id, target_user_id)
    db.commit()
