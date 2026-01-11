from __future__ import annotations

from abc import ABCMeta, abstractmethod
from typing import TYPE_CHECKING

from .database_tables import Base

if TYPE_CHECKING:
    from typing import Self


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
        raise NotImplementedError(
            (
                f"A `{__name__}` method of the `{self.__class__.__name__}` "
                f"interface must be implemented"
            )
        )
