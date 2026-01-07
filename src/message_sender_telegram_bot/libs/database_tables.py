from typing import final
from uuid import UUID

from sqlalchemy import String
from sqlalchemy.orm import (
    DeclarativeBase,
    Mapped,
    MappedAsDataclass,
    mapped_column,
)


class Base(  # pyright: ignore[reportUnsafeMultipleInheritance]  # type: ignore
    MappedAsDataclass, DeclarativeBase
):
    pass


# TODO make a relationship between the `User` and `ValidToken` tables
@final
class User(Base):
    __tablename__ = "user"

    id_: Mapped[UUID] = mapped_column("id", primary_key=True)
    user_id: Mapped[int]
    token: Mapped[str | None] = mapped_column(String(64))
    # An object that contains a DB column with a valid token
    is_authorizing: Mapped[bool]


@final
class ValidToken(Base):
    __tablename__ = "valid_token"

    id_: Mapped[UUID] = mapped_column("id", primary_key=True)
    token: Mapped[str] = mapped_column(String(64))
