from __future__ import annotations

from typing import TYPE_CHECKING, override

from sqlalchemy import select

from .database_tables import ValidToken
from .db_item_getter import DBItemGetter

if TYPE_CHECKING:
    from typing import Self

    from sqlalchemy import Select
    from sqlalchemy.orm import Session


class DBValidTokenGetter(DBItemGetter):
    """
    A DB valid token getter.

    :param DBItemGetter: A DB item getter interface.
    :type DBItemGetter: class
    """

    def __init__(self: Self, db_session: Session, token: str) -> None:
        """
        Creates a DB valid token getter.

        :param db_session: A DB session.
        :type db_session: Session
        :param token: A token.
        :type token: str
        """
        self.__db_session: Session = db_session
        self.__token: str = token

    @override
    def get(self: Self) -> ValidToken | None:
        """
        Gets a DB valid token.

        :return: A DB valid token or None, if the DB valid token is not
                 found.
        :rtype: ValidToken | None
        """
        select_token_stmt: Select[tuple[ValidToken]] = select(
            ValidToken
        ).where(ValidToken.token == self.__token)
        valid_token: ValidToken | None = self.__db_session.execute(
            select_token_stmt
        ).scalar_one_or_none()

        return valid_token
