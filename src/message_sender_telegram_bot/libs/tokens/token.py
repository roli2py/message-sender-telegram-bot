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

        :raises NotImplementedError: Must to be implemented.
        :return: A token.
        :rtype: str
        """
        raise NotImplementedError
