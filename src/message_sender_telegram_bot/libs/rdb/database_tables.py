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


class Base(MappedAsDataclass, DeclarativeBase):
    metadata = MetaData(naming_convention=convention)


@final
class User(Base):
    __tablename__ = "user"

    id_: Mapped[UUID] = mapped_column("id", primary_key=True)
    user_id: Mapped[int] = mapped_column(BigInteger)
    is_authorizing: Mapped[bool]
    token_id: Mapped[UUID | None] = mapped_column(
        ForeignKey("valid_token.id", onupdate="CASCADE", ondelete="SET NULL")
    )
    valid_token: Mapped["ValidToken | None"] = relationship(
        back_populates="user"
    )
    is_owner: Mapped[bool]
    last_send_date: Mapped[datetime | None]
    messages: Mapped[list["Message"]] = relationship(back_populates="sender")


@final
class ValidToken(Base):
    __tablename__ = "valid_token"

    id_: Mapped[UUID] = mapped_column("id", primary_key=True)
    token: Mapped[str] = mapped_column(String(64))
    user: Mapped["User | None"] = relationship(back_populates="valid_token")


@final
class Message(Base):
    __tablename__ = "message"

    id_: Mapped[UUID] = mapped_column("id", primary_key=True)
    message_id: Mapped[int] = mapped_column(BigInteger)
    # When the program create a message, the `sender` attribute will set
    # up the `sender_id`, so the `sender_id` can be `None` in code, but
    # `NOT NULL` in DB
    sender_id: Mapped[UUID | None] = mapped_column(
        ForeignKey("user.id", onupdate="CASCADE", ondelete="RESTRICT"),
        nullable=False,
    )
    sender: Mapped[User] = relationship(back_populates="messages")
    text: Mapped[str] = mapped_column(String(4096))
    is_sent: Mapped[bool]
