"""add course recommendation fields (Phase 7)

Revision ID: 20260915_090000
Revises: 20260914_130000
Create Date: 2026-09-15 09:00:00

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision: str = "20260915_090000"
down_revision: Union[str, None] = "20260914_130000"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column(
        "courses",
        sa.Column("difficulty", sa.String(length=20), nullable=False, server_default="중급"),
    )
    op.add_column("courses", sa.Column("green_fee_avg", sa.Integer(), nullable=True))
    op.add_column("courses", sa.Column("tags", sa.String(length=255), nullable=True))


def downgrade() -> None:
    op.drop_column("courses", "tags")
    op.drop_column("courses", "green_fee_avg")
    op.drop_column("courses", "difficulty")
