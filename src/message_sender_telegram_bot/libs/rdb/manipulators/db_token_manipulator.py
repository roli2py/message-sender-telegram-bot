from __future__ import annotations

from logging import getLogger
from typing import TYPE_CHECKING, override
from uuid import uuid4

from sqlalchemy import select

from ...interfaces import DBItemCreator, DBItemGetter
from ..database_tables import Token

if TYPE_CHECKING:
    from logging import Logger
    from typing import Self

    from sqlalchemy import Result, Select
    from sqlalchemy.orm import Session

logger: Logger = getLogger(__name__)


class DBTokenManipulator(DBItemGetter, DBItemCreator):
    """
    A DB token manipulator.

    :param DBItemGetter: A DB item getter interface.
    :type DBItemGetter: class
    :param DBItemCreator: A DB item creator interface.
    :type DBItemCreator: class
    """

    def __init__(self: Self, db_session: Session, token: str) -> None:
        """
        Creates a DB token manipulator.

        :param db_session: A DB session.
        :type db_session: Session
        :param token: A token.
        :type token: str
        """
        logger.debug("Initializing `%s`...", self.__class__.__name__)

        logger.debug(
            "Setting the arguments to the corresponding instance attributes..."
        )
        self.__db_session: Session = db_session
        self.__token: str = token
        logger.debug("Set")

        logger.debug("Initialized")

    @override
    def get(self: Self) -> Token | None:
        """
        Gets a DB token.

        :return: A DB token or None, if the DB token is not found.
        :rtype: Token | None
        """
        logger.debug("Starting a getting of the DB token...")

        logger.debug("Constructing a statement...")
        select_token_stmt: Select[tuple[Token]] = select(Token).where(
            Token.token == self.__token
        )
        logger.debug("Constructed")

        logger.debug("Executing the statement...")
        result: Result[tuple[Token]] = self.__db_session.execute(
            select_token_stmt
        )
        logger.debug("Executed")

        logger.debug("Getting the DB token...")
        token: Token | None = result.scalar_one_or_none()
        logger.debug("Got")

        return token

    @override
    def create(self: Self) -> Token:
        logger.debug("Starting a creation of the DB token...")

        logger.debug("Creating a DB token...")
        new_token: Token = Token(
            id_=uuid4(),
            token=self.__token,
            user=None,
        )
        logger.debug("Created")

        return new_token
