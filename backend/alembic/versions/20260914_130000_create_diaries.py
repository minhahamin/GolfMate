"""create diaries

Revision ID: 20260914_130000
Revises: 20260914_120000
Create Date: 2026-09-14 13:00:00

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision: str = "20260914_130000"
down_revision: Union[str, None] = "20260914_120000"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "diaries",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("user_id", sa.Integer(), sa.ForeignKey("users.id", ondelete="CASCADE"), nullable=False),
        sa.Column(
            "round_id", sa.Integer(), sa.ForeignKey("rounds.id", ondelete="SET NULL"), nullable=True
        ),
        sa.Column("raw_text", sa.Text(), nullable=False),
        sa.Column("summary", sa.Text(), nullable=False),
        sa.Column("mood", sa.String(length=50), nullable=False),
        sa.Column("highlights", sa.Text(), nullable=False),
        sa.Column("improvement_points", sa.Text(), nullable=False),
        sa.Column("next_goal", sa.Text(), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column(
            "updated_at",
            sa.DateTime(timezone=True),
            server_default=sa.func.now(),
            onupdate=sa.func.now(),
            nullable=False,
        ),
    )
    op.create_index("ix_diaries_user_id", "diaries", ["user_id"])


def downgrade() -> None:
    op.drop_index("ix_diaries_user_id", table_name="diaries")
    op.drop_table("diaries")
