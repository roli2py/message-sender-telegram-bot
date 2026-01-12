"""Change a data type of the `user_id` column of the `user` table to
`BigInteger`

Revision ID: 11424f7eb1a2
Revises: 00f4eeaccbc2
Create Date: 2026-01-12 23:34:20.456883

"""

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op

# revision identifiers, used by Alembic.
revision: str = "11424f7eb1a2"
down_revision: str | Sequence[str] | None = "00f4eeaccbc2"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    """Upgrade schema."""
    op.alter_column("user", "user_id", type_=sa.BigInteger)


def downgrade() -> None:
    """Downgrade schema."""
    op.alter_column("user", "user_id", type_=sa.Integer)
