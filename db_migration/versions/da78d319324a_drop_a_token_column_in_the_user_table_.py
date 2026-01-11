"""Drop a `token` column in the `user` table, create a `token_id` column
and constrain it with a foreigh key to a `id` column of the
`valid_token` table

Revision ID: da78d319324a
Revises: 7b540a7fa884
Create Date: 2026-01-11 23:13:15.600610

"""

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op

# revision identifiers, used by Alembic.
revision: str = "da78d319324a"
down_revision: str | Sequence[str] | None = "7b540a7fa884"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    """Upgrade schema."""
    op.add_column(
        "user",
        sa.Column(
            "token_id",
            sa.Uuid,
            sa.ForeignKey("valid_token.id", ondelete="SET NULL"),
            nullable=True,
        ),
    )


def downgrade() -> None:
    """Downgrade schema."""
    op.drop_constraint("fk_user_token_id_valid_token", "user", "foreignkey")
    op.drop_column("user", "token_id")
