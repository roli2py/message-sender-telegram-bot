from __future__ import annotations

from abc import ABCMeta, abstractmethod
from logging import getLogger
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from logging import Logger
    from typing import Self

    from ..tokens import Token

logger: Logger = getLogger(__name__)


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
                f"must be implemented"
            )
        )
