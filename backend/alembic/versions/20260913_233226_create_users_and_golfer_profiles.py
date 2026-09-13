"""create users and golfer_profiles

Revision ID: 20260913_233226
Revises:
Create Date: 2026-09-13 23:32:26

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision: str = "20260913_233226"
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "users",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("email", sa.String(length=255), nullable=False),
        sa.Column("hashed_password", sa.String(length=255), nullable=False),
        sa.Column("name", sa.String(length=100), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column(
            "updated_at",
            sa.DateTime(timezone=True),
            server_default=sa.func.now(),
            onupdate=sa.func.now(),
            nullable=False,
        ),
    )
    op.create_index("ix_users_email", "users", ["email"], unique=True)

    op.create_table(
        "golfer_profiles",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column(
            "user_id",
            sa.Integer(),
            sa.ForeignKey("users.id", ondelete="CASCADE"),
            nullable=False,
            unique=True,
        ),
        sa.Column("handicap", sa.Float(), nullable=True),
        sa.Column("average_score", sa.Float(), nullable=True),
        sa.Column("driver_distance", sa.Float(), nullable=True),
        sa.Column("iron_distance", sa.Float(), nullable=True),
        sa.Column("putting_average", sa.Float(), nullable=True),
        sa.Column("fairway_percentage", sa.Float(), nullable=True),
        sa.Column("gir_percentage", sa.Float(), nullable=True),
        sa.Column("preferred_tee", sa.String(length=50), nullable=True),
        sa.Column("goal_score", sa.Integer(), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column(
            "updated_at",
            sa.DateTime(timezone=True),
            server_default=sa.func.now(),
            onupdate=sa.func.now(),
            nullable=False,
        ),
    )


def downgrade() -> None:
    op.drop_table("golfer_profiles")
    op.drop_index("ix_users_email", table_name="users")
    op.drop_table("users")
