"""Add an `is_owner` column to the `User` table

Revision ID: 00f4eeaccbc2
Revises: da78d319324a
Create Date: 2026-01-12 18:01:55.248856

"""

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op

# revision identifiers, used by Alembic.
revision: str = "00f4eeaccbc2"
down_revision: str | Sequence[str] | None = "da78d319324a"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    """Upgrade schema."""
    op.add_column("user", sa.Column("is_owner", sa.Boolean, nullable=False))


def downgrade() -> None:
    """Downgrade schema."""
    op.drop_column("user", "is_owner")
