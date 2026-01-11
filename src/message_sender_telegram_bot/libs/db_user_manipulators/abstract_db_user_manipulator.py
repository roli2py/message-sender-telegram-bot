from __future__ import annotations

from abc import ABCMeta, abstractmethod
from typing import TYPE_CHECKING, override

from ..database_tables import User
from ..db_item_getter import DBItemGetter

if TYPE_CHECKING:
    from typing import Self


class AbstractDBUserManipulator(DBItemGetter, metaclass=ABCMeta):
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
        raise NotImplementedError(
            (
                f"A `{__name__}` method of the `{self.__class__.__name__}` "
                f"interface must be implemented"
            )
        )

    @abstractmethod
    def create(self: Self) -> User:
        """
        Creates a new DB user.

        :return: A new DB user.
        :rtype: User
        :raises NotImplementedError: Must be implemented.
        """
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
        raise NotImplementedError(
            (
                f"A `{__name__}` method of the `{self.__class__.__name__}` "
                f"interface must be implemented"
            )
        )

    @abstractmethod
    def get_token(self: Self) -> str | None:
        """
        Gets a DB user's token.

        :return: A DB user's token or None, if the DB user's token is
                 absent.
        :rtype: str | None
        :raises NotImplementedError: Must be implemented.
        """
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
        raise NotImplementedError(
            (
                f"A `{__name__}` method of the `{self.__class__.__name__}` "
                f"interface must be implemented"
            )
        )

    @abstractmethod
    def set_token(self: Self, token: str) -> None:
        """
        Sets a DB user's token. This means, that the user claims the
        token.

        :param token: A token to set.
        :type token: str
        :raises NotImplementedError: Must be implemented.
        """
        raise NotImplementedError(
            (
                f"A `{__name__}` method of the `{self.__class__.__name__}` "
                f"interface must be implemented"
            )
        )

    @abstractmethod
    def clear_token(self: Self) -> None:
        """
        Clears a DB user's token. This means, that the user loses the
        claim to the token.

        :raises NotImplementedError: Must be implemented.
        """
        raise NotImplementedError(
            (
                f"A `{__name__}` method of the `{self.__class__.__name__}` "
                f"interface must be implemented"
            )
        )
