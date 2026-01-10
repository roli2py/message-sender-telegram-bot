from __future__ import annotations

from abc import ABCMeta, abstractmethod
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from typing import Self

    from ..tokens import Token


class TokenCreator(metaclass=ABCMeta):
    """A token creator interface."""

    @abstractmethod
    def create(self: Self) -> Token:
        """
        Creates a token.

        :raises NotImplementedError: Must to be implemented.
        :return: A token.
        :rtype: Token
        """
        raise NotImplementedError(
            (
                f"A `{__name__}` method of the `{self.__class__.__name__}` "
                f"must be implemented"
            )
        )
