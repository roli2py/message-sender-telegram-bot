"""Create a `Message` table

Revision ID: 6b961863554f
Revises: bc97e89af787
Create Date: 2026-02-16 18:28:08.030449

"""

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op

# revision identifiers, used by Alembic.
revision: str = "6b961863554f"
down_revision: str | Sequence[str] | None = "bc97e89af787"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    """Upgrade schema."""
    op.create_table(
        "message",
        sa.Column("id", sa.Uuid, primary_key=True),
        sa.Column("message_id", sa.BigInteger, nullable=False),
        sa.Column(
            "sender_id",
            sa.Uuid,
            sa.ForeignKey(
                "user.id",
                onupdate="CASCADE",
                ondelete="RESTRICT",
            ),
            nullable=False,
        ),
        sa.Column("text", sa.String(4096), nullable=False),
        sa.Column("is_sent", sa.Boolean, nullable=False),
    )


def downgrade() -> None:
    """Downgrade schema."""
    op.drop_constraint("fk_message_sender_id_user", "message", "foreignkey")
    op.drop_table("message")
