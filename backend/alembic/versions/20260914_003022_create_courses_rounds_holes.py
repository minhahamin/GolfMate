"""create courses, course_holes, rounds, holes

Revision ID: 20260914_003022
Revises: 20260913_233226
Create Date: 2026-09-14 00:30:22

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision: str = "20260914_003022"
down_revision: Union[str, None] = "20260913_233226"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "courses",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("name", sa.String(length=200), nullable=False),
        sa.Column("region", sa.String(length=100), nullable=False),
        sa.Column("address", sa.String(length=255), nullable=True),
        sa.Column("description", sa.Text(), nullable=True),
        sa.Column("holes_count", sa.Integer(), nullable=False, server_default="18"),
        sa.Column("par", sa.Integer(), nullable=False, server_default="72"),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
    )

    op.create_table(
        "course_holes",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column(
            "course_id", sa.Integer(), sa.ForeignKey("courses.id", ondelete="CASCADE"), nullable=False
        ),
        sa.Column("hole_number", sa.Integer(), nullable=False),
        sa.Column("par", sa.Integer(), nullable=False),
        sa.Column("distance_meters", sa.Integer(), nullable=False),
        sa.UniqueConstraint("course_id", "hole_number", name="uq_course_hole_number"),
    )

    op.create_table(
        "rounds",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("user_id", sa.Integer(), sa.ForeignKey("users.id", ondelete="CASCADE"), nullable=False),
        sa.Column("course_id", sa.Integer(), sa.ForeignKey("courses.id"), nullable=False),
        sa.Column("round_date", sa.Date(), nullable=False),
        sa.Column("score", sa.Integer(), nullable=False),
        sa.Column("weather", sa.String(length=50), nullable=True),
        sa.Column("temperature", sa.Float(), nullable=True),
        sa.Column("wind", sa.String(length=50), nullable=True),
        sa.Column("memo", sa.Text(), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column(
            "updated_at",
            sa.DateTime(timezone=True),
            server_default=sa.func.now(),
            onupdate=sa.func.now(),
            nullable=False,
        ),
    )
    op.create_index("ix_rounds_user_id", "rounds", ["user_id"])

    op.create_table(
        "holes",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("round_id", sa.Integer(), sa.ForeignKey("rounds.id", ondelete="CASCADE"), nullable=False),
        sa.Column("hole_number", sa.Integer(), nullable=False),
        sa.Column("par", sa.Integer(), nullable=False),
        sa.Column("score", sa.Integer(), nullable=False),
        sa.Column("putts", sa.Integer(), nullable=False),
        sa.Column("fairway_hit", sa.Boolean(), nullable=False, server_default=sa.false()),
        sa.Column("gir", sa.Boolean(), nullable=False, server_default=sa.false()),
        sa.Column("ob", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("bunker", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("penalty", sa.Integer(), nullable=False, server_default="0"),
        sa.UniqueConstraint("round_id", "hole_number", name="uq_round_hole_number"),
    )


def downgrade() -> None:
    op.drop_table("holes")
    op.drop_index("ix_rounds_user_id", table_name="rounds")
    op.drop_table("rounds")
    op.drop_table("course_holes")
    op.drop_table("courses")
