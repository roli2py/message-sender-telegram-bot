"""Create the `User` and `ValidToken` tables

Revision ID: 7b540a7fa884
Revises:
Create Date: 2026-01-07 23:07:18.904992

"""

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op

# revision identifiers, used by Alembic.
revision: str = "7b540a7fa884"
down_revision: str | Sequence[str] | None = None
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    """Upgrade schema."""
    _ = op.create_table(
        "valid_token",
        sa.Column("id", sa.Uuid, primary_key=True),
        sa.Column("token", sa.String(64), nullable=False),
    )
    _ = op.create_table(
        "user",
        sa.Column("id", sa.Uuid, primary_key=True),
        sa.Column("user_id", sa.Integer, nullable=False),
        sa.Column(
            "token",
            sa.String(64),
            nullable=True,
        ),
        sa.Column("is_authorizing", sa.Boolean, nullable=False),
    )


def downgrade() -> None:
    """Downgrade schema."""
    op.drop_table("user")
    op.drop_table("valid_token")
