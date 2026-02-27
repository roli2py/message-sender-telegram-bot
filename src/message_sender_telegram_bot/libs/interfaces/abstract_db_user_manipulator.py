from __future__ import annotations

from abc import ABCMeta, abstractmethod
from logging import getLogger
from typing import TYPE_CHECKING, override

from .db_item_creator import DBItemCreator
from .db_item_getter import DBItemGetter

if TYPE_CHECKING:
    from logging import Logger
    from typing import Self

    from ..rdb.database_tables import User, ValidToken

logger: Logger = getLogger(__name__)


class AbstractDBUserManipulator(
    DBItemGetter, DBItemCreator, metaclass=ABCMeta
):
    """A DB user manipulator interface."""

    @abstractmethod
    @override
    def get(self: Self) -> User | None:
        """
        Gets a DB user.

        :return: A DB user or None, if the DB user is not found.
        :rtype: User | None
        :raises NotImplementedError: Must be implemented.
        """
        logger.critical(
            (
                "A `%s` method of the `%s` interface in invoked. Raising a "
                "`NotImplementedError` exception..."
            ),
            __name__,
            self.__class__.__name__,
            exc_info=True,
        )
        raise NotImplementedError(
            (
                f"A `{__name__}` method of the `{self.__class__.__name__}` "
                f"interface must be implemented"
            )
        )

    @abstractmethod
    @override
    def create(self: Self) -> User:
        """
        Creates a new DB user.

        :return: A new DB user.
        :rtype: User
        :raises NotImplementedError: Must be implemented.
        """
        logger.critical(
            (
                "A `%s` method of the `%s` interface in invoked. Raising a "
                "`NotImplementedError` exception..."
            ),
            __name__,
            self.__class__.__name__,
            exc_info=True,
        )
        raise NotImplementedError(
            (
                f"A `{__name__}` method of the `{self.__class__.__name__}` "
                f"interface must be implemented"
            )
        )

    @abstractmethod
    def get_authorizing_status(self: Self) -> bool:
        """
        Gets a DB user's authorizing status.

        :return: A DB user's authorizing status.
        :rtype: bool
        :raises NotImplementedError: Must be implemented.
        """
        logger.critical(
            (
                "A `%s` method of the `%s` interface in invoked. Raising a "
                "`NotImplementedError` exception..."
            ),
            __name__,
            self.__class__.__name__,
            exc_info=True,
        )
        raise NotImplementedError(
            (
                f"A `{__name__}` method of the `{self.__class__.__name__}` "
                f"interface must be implemented"
            )
        )

    @abstractmethod
    def get_valid_token(self: Self) -> ValidToken | None:
        """
        Gets a DB user's DB valid token.

        :return: A DB user's DB valid token or None, if the DB user's
                 valid token is absent.
        :rtype: str | None
        :raises NotImplementedError: Must be implemented.
        """
        logger.critical(
            (
                "A `%s` method of the `%s` interface in invoked. Raising a "
                "`NotImplementedError` exception..."
            ),
            __name__,
            self.__class__.__name__,
            exc_info=True,
        )
        raise NotImplementedError(
            (
                f"A `{__name__}` method of the `{self.__class__.__name__}` "
                f"interface must be implemented"
            )
        )

    @abstractmethod
    def set_authorizing_status(self: Self, is_authorizing: bool) -> None:
        """
        Sets a DB user's authorizing status.

        :param is_authorizing: An authorizing status to set.
        :type is_authorizing: bool
        :raises NotImplementedError: Must be implemented.
        """
        logger.critical(
            (
                "A `%s` method of the `%s` interface in invoked. Raising a "
                "`NotImplementedError` exception..."
            ),
            __name__,
            self.__class__.__name__,
            exc_info=True,
        )
        raise NotImplementedError(
            (
                f"A `{__name__}` method of the `{self.__class__.__name__}` "
                f"interface must be implemented"
            )
        )

    @abstractmethod
    def set_valid_token(self: Self, valid_token: ValidToken) -> None:
        """
        Sets a DB user's DB valid token. This means, that the user
        claims the token.

        :param token: A DB valid token to set.
        :type token: str
        :raises NotImplementedError: Must be implemented.
        """
        logger.critical(
            (
                "A `%s` method of the `%s` interface in invoked. Raising a "
                "`NotImplementedError` exception..."
            ),
            __name__,
            self.__class__.__name__,
            exc_info=True,
        )
        raise NotImplementedError(
            (
                f"A `{__name__}` method of the `{self.__class__.__name__}` "
                f"interface must be implemented"
            )
        )

    @abstractmethod
    def clear_valid_token(self: Self) -> None:
        """
        Clears a DB user's DB valid token. This means, that the user
        loses the claim to the token.

        :raises NotImplementedError: Must be implemented.
        """
        logger.critical(
            (
                "A `%s` method of the `%s` interface in invoked. Raising a "
                "`NotImplementedError` exception..."
            ),
            __name__,
            self.__class__.__name__,
            exc_info=True,
        )
        raise NotImplementedError(
            (
                f"A `{__name__}` method of the `{self.__class__.__name__}` "
                f"interface must be implemented"
            )
        )

    @abstractmethod
    def get_owner_status(self: Self) -> bool:
        """
        Gets a DB user's owner status. That is, is the user owner or
        not.

        :return: A DB user's owner status.
        :rtype: bool
        :raises NotImplementedError: Must be implemented.
        """
        logger.critical(
            (
                "A `%s` method of the `%s` interface in invoked. Raising a "
                "`NotImplementedError` exception..."
            ),
            __name__,
            self.__class__.__name__,
            exc_info=True,
        )
        raise NotImplementedError(
            (
                f"A `{__name__}` method of the `{self.__class__.__name__}` "
                f"interface must be implemented"
            )
        )
