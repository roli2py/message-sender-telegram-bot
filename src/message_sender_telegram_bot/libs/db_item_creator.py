from __future__ import annotations

from abc import ABCMeta, abstractmethod
from logging import getLogger
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from logging import Logger
    from typing import Self

    from .database_tables import Base

logger: Logger = getLogger(__name__)


class DBItemCreator(metaclass=ABCMeta):
    """A DB item creator interface."""

    @abstractmethod
    def create(self: Self) -> Base:
        """
        Creates a new DB item.

        :return: A new DB item.
        :rtype: Base
        :raises NotImplementedError: Must be implemented.
        """
        logger.critical(
            (
                f"A `%s` method of the `%s` interface is invoked. Raising a "
                f"`NotImplementedError` exception..."
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
