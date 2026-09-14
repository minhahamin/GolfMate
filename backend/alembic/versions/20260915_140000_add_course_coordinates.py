"""add course coordinates for weather lookup (Phase 8)

Revision ID: 20260915_140000
Revises: 20260915_090000
Create Date: 2026-09-15 14:00:00

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision: str = "20260915_140000"
down_revision: Union[str, None] = "20260915_090000"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column("courses", sa.Column("latitude", sa.Float(), nullable=True))
    op.add_column("courses", sa.Column("longitude", sa.Float(), nullable=True))


def downgrade() -> None:
    op.drop_column("courses", "longitude")
    op.drop_column("courses", "latitude")
