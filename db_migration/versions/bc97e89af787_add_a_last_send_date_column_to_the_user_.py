"""Add a `last_send_date` column to the `User` table

Revision ID: bc97e89af787
Revises: 11424f7eb1a2
Create Date: 2026-01-13 20:16:49.998528

"""

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op

# revision identifiers, used by Alembic.
revision: str = "bc97e89af787"
down_revision: str | Sequence[str] | None = "11424f7eb1a2"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    """Upgrade schema."""
    op.add_column(
        "user", sa.Column("last_send_date", sa.DateTime, nullable=True)
    )


def downgrade() -> None:
    """Downgrade schema."""
    op.drop_column("user", "last_send_date")
