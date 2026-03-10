"""Rename `ValidToken` to `Token` and update corresponding occurs of
this table

Revision ID: 158c8310c382
Revises: 6b961863554f
Create Date: 2026-03-10 16:08:34.564802

"""

from collections.abc import Sequence

from alembic import op

# revision identifiers, used by Alembic.
revision: str = "158c8310c382"
down_revision: str | Sequence[str] | None = "6b961863554f"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    """Upgrade schema."""
    op.drop_constraint(
        "fk_user_token_id_valid_token",
        "user",
        "foreignkey",
    )
    op.rename_table("valid_token", "token")
    op.create_foreign_key(
        None,
        "user",
        "token",
        ["token_id"],
        ["id"],
    )


def downgrade() -> None:
    """Downgrade schema."""
    op.drop_constraint(
        "fk_user_token_id_token",
        "user",
        "foreignkey",
    )
    op.rename_table("token", "valid_token")
    op.create_foreign_key(
        None,
        "user",
        "valid_token",
        ["token_id"],
        ["id"],
    )
