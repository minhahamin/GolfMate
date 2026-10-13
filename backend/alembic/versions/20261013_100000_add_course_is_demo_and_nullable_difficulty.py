"""add courses.is_demo, make difficulty nullable (real golf course data)

Revision ID: 20261013_100000
Revises: 20260915_180000
Create Date: 2026-10-13 10:00:00

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision: str = "20261013_100000"
down_revision: Union[str, None] = "20260915_180000"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column(
        "courses",
        sa.Column("is_demo", sa.Boolean(), nullable=False, server_default=sa.false()),
    )
    op.alter_column(
        "courses", "difficulty", existing_type=sa.String(length=20), nullable=True, server_default=None
    )
    # 기존 가상 코스(seed_courses.py)는 주소에 "(가상 주소)"가 들어 있다.
    op.execute("UPDATE courses SET is_demo = true WHERE address LIKE '%(가상 주소)%'")


def downgrade() -> None:
    op.execute("UPDATE courses SET difficulty = '중급' WHERE difficulty IS NULL")
    op.alter_column(
        "courses", "difficulty", existing_type=sa.String(length=20), nullable=False, server_default="중급"
    )
    op.drop_column("courses", "is_demo")
