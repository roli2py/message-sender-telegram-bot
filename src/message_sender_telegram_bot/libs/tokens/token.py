from __future__ import annotations

from abc import ABCMeta, abstractmethod
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from typing import Self


class Token(metaclass=ABCMeta):
    """A token interface."""

    @abstractmethod
    def get(self: Self) -> str:
        """
        Returns a token.

        :return: A token.
        :rtype: str
        :raises NotImplementedError: Must to be implemented.
        """
        raise NotImplementedError(
            (
                f"A {__name__} method of the {self.__class__.__name__} "
                f"interface must be implemented"
            )
        )
