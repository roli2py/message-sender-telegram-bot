from datetime import datetime
from typing import final
from uuid import UUID

from sqlalchemy import BigInteger, ForeignKey, MetaData, String
from sqlalchemy.orm import (
    DeclarativeBase,
    Mapped,
    MappedAsDataclass,
    mapped_column,
    relationship,
)

# Reference: https://docs.sqlalchemy.org/en/20/core/constraints.html#configuring-a-naming-convention-for-a-metadata-collection
convention: dict[str, str] = {
    "ix": "ix_%(column_0_label)s",
    "uq": "uq_%(table_name)s_%(column_0_name)s",
    "ck": "ck_%(table_name)s_%(constraint_name)s",
    "fk": "fk_%(table_name)s_%(column_0_name)s_%(referred_table_name)s",
    "pk": "pk_%(table_name)s",
}


class Base(  # pyright: ignore[reportUnsafeMultipleInheritance]  # type: ignore
    MappedAsDataclass, DeclarativeBase
):
    metadata = MetaData(  # pyright: ignore[reportUnannotatedClassAttribute]  # type: ignore
        naming_convention=convention
    )


@final
class User(Base):
    __tablename__ = "user"

    id_: Mapped[UUID] = mapped_column("id", primary_key=True)
    user_id: Mapped[int] = mapped_column(BigInteger)
    is_authorizing: Mapped[bool]
    token_id: Mapped[UUID | None] = mapped_column(
        ForeignKey("valid_token.id", ondelete="SET NULL")
    )
    valid_token: Mapped["ValidToken | None"] = relationship(
        back_populates="user"
    )
    is_owner: Mapped[bool]
    last_send_date: Mapped[datetime | None]


@final
class ValidToken(Base):
    __tablename__ = "valid_token"

    id_: Mapped[UUID] = mapped_column("id", primary_key=True)
    token: Mapped[str] = mapped_column(String(64))
    user: Mapped["User | None"] = relationship(back_populates="valid_token")
