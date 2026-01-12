from __future__ import annotations

from logging import getLogger
from typing import TYPE_CHECKING, override
from uuid import uuid4

from sqlalchemy import select

from .database_tables import ValidToken
from .db_item_creator import DBItemCreator
from .db_item_getter import DBItemGetter

if TYPE_CHECKING:
    from logging import Logger
    from typing import Self

    from sqlalchemy import Result, Select
    from sqlalchemy.orm import Session

logger: Logger = getLogger(__name__)


class DBValidTokenManipulator(DBItemGetter, DBItemCreator):
    """
    A DB valid token manipulator.

    :param DBItemGetter: A DB item getter interface.
    :type DBItemGetter: class
    :param DBItemCreator: A DB item creator interface.
    :type DBItemCreator: class
    """

    def __init__(self: Self, db_session: Session, token: str) -> None:
        """
        Creates a DB valid token manipulator.

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
    def get(self: Self) -> ValidToken | None:
        """
        Gets a DB valid token.

        :return: A DB valid token or None, if the DB valid token is not
                 found.
        :rtype: ValidToken | None
        """
        logger.debug("Starting a getting of the DB valid token...")

        logger.debug("Constructing a statement...")
        select_token_stmt: Select[tuple[ValidToken]] = select(
            ValidToken
        ).where(ValidToken.token == self.__token)
        logger.debug("Constructed")

        logger.debug("Executing the statement...")
        result: Result[tuple[ValidToken]] = self.__db_session.execute(
            select_token_stmt
        )
        logger.debug("Executed")

        logger.debug("Getting the DB valid token...")
        valid_token: ValidToken | None = result.scalar_one_or_none()
        logger.debug("Got")

        return valid_token

    @override
    def create(self: Self) -> ValidToken:
        logger.debug("Starting a creation of the DB valid token...")

        logger.debug("Creating a DB valid token...")
        new_valid_token: ValidToken = ValidToken(
            id_=uuid4(),
            token=self.__token,
            user=None,
        )
        logger.debug("Created")

        return new_valid_token
