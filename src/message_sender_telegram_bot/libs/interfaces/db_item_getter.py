from __future__ import annotations

from abc import ABCMeta, abstractmethod
from logging import getLogger
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from logging import Logger
    from typing import Self

    from ..rdb.database_tables import Base

logger: Logger = getLogger(__name__)


class DBItemGetter(metaclass=ABCMeta):
    """A DB item getter interface."""

    @abstractmethod
    def get(self: Self) -> Base | None:
        """
        Gets a DB item.

        :return: A DB item or None, if the DB item is not found.
        :rtype: Base | None
        :raises NotImplementedError: Must be implemented.
        """
        logger.critical(
            (
                "A `%s` method of the `%s` interface is invoked. Raising a "
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
