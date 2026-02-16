from __future__ import annotations

from logging import getLogger
from typing import TYPE_CHECKING, overload, override
from uuid import uuid4

from sqlalchemy import select

from ..database_tables import User, ValidToken
from .abstract_db_user_manipulator import AbstractDBUserManipulator

if TYPE_CHECKING:
    from logging import Logger
    from typing import Self

    from sqlalchemy import Result, Select
    from sqlalchemy.orm import Session

logger: Logger = getLogger(__name__)


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
        logger.debug("Initializing `%s`...", self.__class__.__name__)

        logger.debug(
            (
                "Checking an absent or a presence of the `user_id` and "
                "`db_user` arguments..."
            )
        )
        if user_id is None and db_user is None:
            logger.critical(
                (
                    "The `user_id` and `db_user` arguments is absent. "
                    "Raising a `ValueError` exception..."
                ),
                exc_info=True,
            )
            raise ValueError("A user ID or a DB user must be provided")
        elif user_id is not None and db_user is not None:
            logger.critical(
                (
                    "The `user_id` and `db_user` arguments is present. "
                    "Raising a `ValueError` exception..."
                ),
                exc_info=True,
            )
            raise ValueError("Only a user ID or a DB user must be provided")
        logger.debug(
            (
                "Only a `user_id` or `db_user` argument is provided. "
                "Continuing an initializing..."
            )
        )

        logger.debug(
            (
                "Assigning the arguments to the corresponding instance "
                "attributes..."
            )
        )
        self.__db_session: Session = db_session
        self.__user_id: int | None = user_id
        self.__db_user: User | None = db_user
        logger.debug("Assigned")
        logger.debug("Initialized")

    @override
    def get(self: Self) -> User | None:
        """
        Gets a DB user by a user ID. That is, selects a DB user where a
        DB user's ID equals to a provided user ID.

        After the invoke, the `db_user` is set and, therefore, can be
        used to invoke methods that require a DB user.

        :return: A DB user or None, if the DB user is not found.
        :rtype: User | None
        """
        logger.debug("Starting a getting of a DB user...")
        user_id: int | None = self.__user_id

        logger.debug("Checking for a presence of a user ID...")
        if user_id is None:
            logger.critical(
                "A user ID is absent. Raising a `ValueError` exception..."
            )
            raise ValueError("A user ID is absent")
        logger.debug(
            "A user ID is present. Continuing the getting of the DB user..."
        )

        logger.debug("Constructing a DB statement...")
        select_user_stmt: Select[tuple[User]] = select(User).where(
            User.user_id == self.__user_id
        )
        logger.debug("Constructed")
        logger.debug("Executing the statement...")
        result: Result[tuple[User]] = self.__db_session.execute(
            select_user_stmt
        )
        logger.debug("Executed")
        logger.debug("Getting the DB user....")
        db_user: User | None = result.scalar_one_or_none()
        logger.debug("Got")

        logger.debug(
            "Assigning the DB user to the `__db_user` instance attribute..."
        )
        self.__db_user = db_user
        logger.debug("Assigned")

        return db_user

    @override
    def create(self: Self) -> User:
        """
        Creates a new DB user without a token and with an authorizing
        status — True by a user ID.

        After the invoke, the `db_user` is set and, therefore, can be
        used to invoke methods that require a DB user.

        :return: A new DB user.
        :rtype: User
        """
        logger.debug("Starting a creation of a new DB user...")
        user_id: int | None = self.__user_id

        logger.debug("Checking for a presence of a user ID...")
        if user_id is None:
            logger.critical(
                "A user ID is absent. Raising a `ValueError` exception..."
            )
            raise ValueError("A user ID is absent")
        logger.debug(
            "A user ID is present. Continuing the creation of the DB user..."
        )

        logger.debug("Creating a DB user...")
        new_db_user: User = User(
            id_=uuid4(),
            user_id=user_id,
            is_authorizing=True,
            token_id=None,
            valid_token=None,
            is_owner=False,
            last_send_date=None,
            messages=[],
        )
        logger.debug("Created")

        logger.debug(
            "Assigning the DB user to the `__db_user` instance attribute..."
        )
        self.__db_user = new_db_user
        logger.debug("Assigned")

        return new_db_user

    @override
    def get_authorizing_status(self: Self) -> bool:
        """
        Gets a DB user's authorizing status. That is, gets an
        `is_authorizing` column.

        :return: A DB user's authorizing status.
        :rtype: bool
        """
        logger.debug("Starting a getting of an authorizing status...")
        db_user: User | None = self.__db_user

        logger.debug("Checking for a presence of a DB user...")
        if db_user is None:
            logger.critical(
                "A DB user is absent. Raising a `ValueError` exception..."
            )
            raise ValueError("A DB user is absent")
        logger.debug(
            (
                "A DB user is present. Continuing the getting of the "
                "authorizing status..."
            )
        )

        logger.debug("Getting an authorizing status...")
        is_user_authorizing: bool = db_user.is_authorizing
        logger.debug("Got")

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
        logger.debug("Starting a getting of a DB valid token...")
        db_user: User | None = self.__db_user

        logger.debug("Checking for a presence of a DB user...")
        if db_user is None:
            logger.critical(
                "A DB user is absent. Raising a `ValueError` exception..."
            )
            raise ValueError("A DB user is absent")
        logger.debug(
            (
                "A DB user is present. Continuing the getting of the DB valid "
                "token..."
            )
        )

        logger.debug("Getting a DB valid token...")
        valid_token: ValidToken | None = db_user.valid_token
        logger.debug("Got")

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
        logger.debug("Starting a setting of an authorizing status...")
        db_user: User | None = self.__db_user

        logger.debug("Checking for a presence of a DB user...")
        if db_user is None:
            logger.critical(
                "A DB user is absent. Raising a `ValueError` exception..."
            )
            raise ValueError("A DB user is absent")
        logger.debug(
            (
                "A DB user is present. Continuing the setting of the "
                "authorizing status..."
            )
        )

        logger.debug("Setting an authorizing status...")
        db_user.is_authorizing = is_authorizing
        logger.debug("Set")

    @override
    def set_valid_token(self: Self, valid_token: ValidToken) -> None:
        """
        Sets a DB user's DB valid token. That is, sets a `token_id` to
        a corresponding row in the `valid_token` table. This means, that
        the user claims the token.

        :param token: A DB valid token to set.
        :type token: str
        """
        logger.debug("Starting a setting of a DB valid token...")
        db_user: User | None = self.__db_user

        logger.debug("Checking for a presence of a DB user...")
        if db_user is None:
            logger.critical(
                "A DB user is absent. Raising a `ValueError` exception..."
            )
            raise ValueError("A DB user is absent")
        logger.debug(
            (
                "A DB user is present. Continuing the setting of the DB valid "
                "token..."
            )
        )

        logger.debug("Setting a DB valid token...")
        db_user.valid_token = valid_token
        logger.debug("Set")

    @override
    def clear_valid_token(self: Self) -> None:
        """
        Clears a DB user's DB valid token. That is, sets a `token_id`
        column to `None`. This means, that the user loses the claim to
        the token.
        """
        logger.debug("Starting a clearing of the DB valid token...")
        db_user: User | None = self.__db_user

        logger.debug("Checking for a presence of a DB user...")
        if db_user is None:
            logger.critical(
                "A DB user is absent. Raising a `ValueError` exception..."
            )
            raise ValueError("A DB user is absent")
        logger.debug(
            (
                "A DB user is present. Continuing the clearing of the DB "
                "valid token..."
            )
        )

        logger.debug("Clearing the DB valid token...")
        db_user.valid_token = None
        logger.debug("Cleared")

    @override
    def get_owner_status(self: Self) -> bool:
        """
        Gets a DB user's owner status. That is, is the user owner or
        not.

        :return: A DB user's owner status.
        :rtype: bool
        :raises NotImplementedError: Must be implemented.
        """
        logger.debug("Starting a getting of an owner status...")
        db_user: User | None = self.__db_user

        logger.debug("Checking for a presence of a DB user...")
        if db_user is None:
            logger.critical(
                "A DB user is absent. Raising a `ValueError` exception..."
            )
            raise ValueError("A DB user is absent")
        logger.debug(
            (
                "A DB user is present. Continuing the clearing of the DB "
                "valid token..."
            )
        )

        logger.debug("Getting an owner status...")
        is_user_owner: bool = db_user.is_owner
        logger.debug("Got")

        return is_user_owner
