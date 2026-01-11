from __future__ import annotations

from typing import TYPE_CHECKING, overload, override
from uuid import uuid4

from sqlalchemy import select

from ..database_tables import User, ValidToken
from .abstract_db_user_manipulator import AbstractDBUserManipulator

if TYPE_CHECKING:
    from typing import Self

    from sqlalchemy import Select
    from sqlalchemy.orm import Session


class DBUserManipulator(AbstractDBUserManipulator):
    """
    A DB user manipulator.

    :param AbstractDBUserManipulator: A DB user manipulator interface.
    :type AbstractDBUserManipulator: class
    """

    @overload
    def __init__(
        self: Self,
        db_session: Session,
        *,
        user_id: int,
    ) -> None: ...

    @overload
    def __init__(
        self: Self,
        db_session: Session,
        *,
        db_user: User,
    ) -> None: ...

    def __init__(
        self: Self,
        db_session: Session,
        *,
        user_id: int | None = None,
        db_user: User | None = None,
    ) -> None:
        """
        Creates a DB user manipulator.

        :param db_session: A DB session.
        :type db_session: Session
        :param user_id: A user ID, defaults to None. Either a user ID or
                        a DB user must be provided but not both.
        :type user_id: int | None, optional
        :param db_user: A DB user, defaults to None. Either a user ID or
                        a DB user must be provided but not both.
        :type db_user: User | None, optional
        :raises ValueError: Either nothing or both user ID and DB user
                            are provided.
        """
        # There is no reason to supply both user ID and DB user, because
        # the class creates a DB user from a user ID or a client
        # directly provides a DB user; so the constructor checks the
        # cases when a client doesn't supply a user ID or DB user, or
        # supplies them both
        if user_id is None and db_user is None:
            raise ValueError("A user ID or a DB user must be provided")
        elif user_id is not None and db_user is not None:
            raise ValueError("Only a user ID or a DB user must be provided")
        self.__db_session: Session = db_session
        self.__user_id: int | None = user_id
        self.__db_user: User | None = db_user

    @override
    def get(self: Self) -> User | None:
        """
        Gets a DB user by a user ID. That is, selects a DB user where a
        DB user's ID equals to a provided user ID.

        :return: A DB user or None, if the DB user is not found.
        :rtype: User | None
        """
        user_id: int | None = self.__user_id

        if user_id is None:
            raise ValueError("A user ID is absent")

        select_user_stmt: Select[tuple[User]] = select(User).where(
            User.user_id == self.__user_id
        )
        db_user: User | None = self.__db_session.execute(
            select_user_stmt
        ).scalar_one_or_none()

        self.__db_user = db_user

        return db_user

    @override
    def create(self: Self) -> User:
        """
        Creates a new DB user without a token and with an authorizing
        status — True by a user ID.

        :return: A new DB user.
        :rtype: User
        """
        user_id: int | None = self.__user_id

        if user_id is None:
            raise ValueError("A user ID is absent")

        new_db_user: User = User(
            id_=uuid4(),
            user_id=user_id,
            is_authorizing=True,
            token_id=None,
            valid_token=None,
        )

        return new_db_user

    @override
    def get_authorizing_status(self: Self) -> bool:
        """
        Gets a DB user's authorizing status. That is, gets an
        `is_authorizing` column.

        :return: A DB user's authorizing status.
        :rtype: bool
        """
        db_user: User | None = self.__db_user

        if db_user is None:
            raise ValueError("A DB user is absent")

        is_user_authorizing: bool = db_user.is_authorizing
        print(is_user_authorizing)

        return is_user_authorizing

    @override
    def get_valid_token(self: Self) -> ValidToken | None:
        """
        Gets a DB user's DB valid token. That is, gets a `ValidToken`
        object.

        :return: A DB user's DB valid token or None, if the DB user's DB
                 valid token is absent.
        :rtype: str | None
        """
        db_user: User | None = self.__db_user

        if db_user is None:
            raise ValueError("A DB user is absent")

        valid_token: ValidToken | None = db_user.valid_token

        return valid_token

    @override
    def set_authorizing_status(self: Self, is_authorizing: bool) -> None:
        """
        Sets a DB user's authorizing status. That is, sets an
        `is_authorizing` column to the `is_authorizing` argument's
        value.

        :param is_authorizing: An authorizing status to set.
        :type is_authorizing: bool
        """
        db_user: User | None = self.__db_user

        if db_user is None:
            raise ValueError("A DB user is absent")

        db_user.is_authorizing = is_authorizing

    @override
    def set_valid_token(self: Self, valid_token: ValidToken) -> None:
        """
        Sets a DB user's DB valid token. That is, sets a `token_id` to
        a corresponding row in the `valid_token` table. This means, that
        the user claims the token.

        :param token: A DB valid token to set.
        :type token: str
        """
        db_user: User | None = self.__db_user

        if db_user is None:
            raise ValueError("A DB user is absent")

        db_user.valid_token = valid_token

    @override
    def clear_valid_token(self: Self) -> None:
        """
        Clears a DB user's DB valid token. That is, sets a `token_id`
        column to `None`. This means, that the user loses the claim to
        the token.
        """
        db_user: User | None = self.__db_user

        if db_user is None:
            raise ValueError("A DB user is absent")

        db_user.valid_token = None
