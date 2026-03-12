from __future__ import annotations

from logging import getLogger
from typing import TYPE_CHECKING, override
from uuid import uuid4

from sqlalchemy import select

from ...interfaces import DBItemCreator, DBItemGetter
from ..database_tables import Message, User

if TYPE_CHECKING:
    from logging import Logger
    from typing import Self

    from sqlalchemy import Result, Select
    from sqlalchemy.orm import Session

logger: Logger = getLogger(__name__)


class DBMessageManipulator(DBItemGetter, DBItemCreator):
    """
    A DB message manipulator.

    :param DBItemGetter: A DB item getter interface.
    :type DBItemGetter: class
    :param DBItemCreator: A DB item creator interface.
    :type DBItemCreator: class
    """

    def __init__(
        self: Self,
        db_session: Session,
        message_id: int,
        *,
        sender: User | None = None,
        text: str | None = None,
    ) -> None:
        """
        Creates a DB message manipulator.

        :param db_session: A DB session.
        :type db_session: Session
        :param message_id: A message ID.
        :type message_id: str
        :param sender: A sender, defaults to None. Must be provided if
                       a program will be creating a new DB message.
        :type sender: User | None
        :param text: A message text, defaults to None. Must be provided
                     if a program will be creating a new DB message.
        :type text: str | None
        """
        logger.debug("Initializing `%s`...", self.__class__.__name__)

        logger.debug(
            "Setting the arguments to the corresponding instance attributes..."
        )
        self.__db_session: Session = db_session
        self.__message_id: int = message_id
        self.__sender: User | None = sender
        self.__text: str | None = text
        logger.debug("Set")

        logger.debug("Initialized")

    @override
    def get(self: Self) -> Message | None:
        """
        Gets a DB message.

        :return: A DB message or None, if the DB message is not found.
        :rtype: Message | None
        """
        logger.debug("Starting a getting of the DB message...")

        logger.debug("Constructing a statement...")
        select_message_stmt: Select[tuple[Message]] = select(Message).where(
            Message.message_id == self.__message_id
        )
        logger.debug("Constructed")

        logger.debug("Executing the statement...")
        result: Result[tuple[Message]] = self.__db_session.execute(
            select_message_stmt
        )
        logger.debug("Executed")

        logger.debug("Getting the DB message...")
        message: Message | None = result.scalar_one_or_none()
        logger.debug("Got")

        return message

    @override
    def create(self: Self) -> Message:
        logger.debug("Starting a creation of the DB message...")
        sender: User | None = self.__sender
        text: str | None = self.__text

        logger.debug("Checking for a presence of a sender...")
        if sender is None:
            logger.critical(
                "A sender is absent. Raising a `ValueError` exception..."
            )
            raise ValueError("A sender is absent")
        logger.debug("A sender is present")

        logger.debug("Checking for a presence of a message text...")
        if text is None:
            logger.critical(
                "A message text is absent. Raising a `ValueError` exception..."
            )
            raise ValueError("A message text is absent")
        logger.debug(
            (
                "A message text is present. Continuing the creationg of the "
                "DB message..."
            )
        )

        logger.debug("Creating a DB message...")
        new_message: Message = Message(
            id_=uuid4(),
            message_id=self.__message_id,
            sender_id=None,
            sender=sender,
            text=text,
            is_sent=False,
        )
        logger.debug("Created")

        return new_message
