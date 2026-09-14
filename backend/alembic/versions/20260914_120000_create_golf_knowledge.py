"""create golf_knowledge (pgvector)

Revision ID: 20260914_120000
Revises: 20260914_003022
Create Date: 2026-09-14 12:00:00

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from pgvector.sqlalchemy import Vector

# revision identifiers, used by Alembic.
revision: str = "20260914_120000"
down_revision: Union[str, None] = "20260914_003022"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None

# app/models/golf_knowledge.py의 EMBEDDING_DIM과 반드시 일치해야 한다
# (intfloat/multilingual-e5-small 임베딩 차원).
EMBEDDING_DIM = 384


def upgrade() -> None:
    op.execute("CREATE EXTENSION IF NOT EXISTS vector")

    op.create_table(
        "golf_knowledge",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("category", sa.String(length=50), nullable=False),
        sa.Column("title", sa.String(length=200), nullable=False, unique=True),
        sa.Column("content", sa.Text(), nullable=False),
        sa.Column("embedding", Vector(EMBEDDING_DIM), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
    )


def downgrade() -> None:
    op.drop_table("golf_knowledge")
    op.execute("DROP EXTENSION IF EXISTS vector")
