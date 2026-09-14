"""Group/GroupMember 테이블 접근 전용 계층.

모든 조회 함수는 반드시 user_id(멤버십)로 필터링한다 — 멤버가 아닌 그룹은 절대 반환하지
않는다 (Round와 동일한 404-not-403 원칙).
"""
from sqlalchemy.orm import Session, selectinload

from app.models.group import Group
from app.models.group_member import GroupMember


def create(db: Session, *, name: str, owner_id: int) -> Group:
    group = Group(name=name, owner_id=owner_id)
    db.add(group)
    db.flush()
    db.add(GroupMember(group_id=group.id, user_id=owner_id))
    db.flush()
    return group


def list_by_user(db: Session, user_id: int) -> list[Group]:
    return (
        db.query(Group)
        .join(GroupMember, GroupMember.group_id == Group.id)
        .filter(GroupMember.user_id == user_id)
        .order_by(Group.created_at.desc())
        .all()
    )


def get_by_id_for_member(db: Session, group_id: int, user_id: int) -> Group | None:
    group = (
        db.query(Group)
        .options(selectinload(Group.members).selectinload(GroupMember.user))
        .filter(Group.id == group_id)
        .first()
    )
    if group is None or not any(m.user_id == user_id for m in group.members):
        return None
    return group


def add_member(db: Session, group_id: int, user_id: int) -> GroupMember:
    member = GroupMember(group_id=group_id, user_id=user_id)
    db.add(member)
    db.flush()
    return member


def remove_member(db: Session, group_id: int, user_id: int) -> None:
    db.query(GroupMember).filter(
        GroupMember.group_id == group_id, GroupMember.user_id == user_id
    ).delete()
    db.flush()


def is_member(db: Session, group_id: int, user_id: int) -> bool:
    return (
        db.query(GroupMember)
        .filter(GroupMember.group_id == group_id, GroupMember.user_id == user_id)
        .first()
        is not None
    )
