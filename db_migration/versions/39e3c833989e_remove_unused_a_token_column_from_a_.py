"""Remove unused a `token` column from a `user` table

Revision ID: 39e3c833989e
Revises: 158c8310c382
Create Date: 2026-03-13 11:45:19.069004

"""

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op

# revision identifiers, used by Alembic.
revision: str = "39e3c833989e"
down_revision: str | Sequence[str] | None = "158c8310c382"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    """Upgrade schema."""
    op.drop_column("user", "token")


def downgrade() -> None:
    """Downgrade schema."""
    op.add_column("user", sa.Column("token", sa.String(64), nullable=True))
