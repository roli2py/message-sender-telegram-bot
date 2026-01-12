from __future__ import annotations

from abc import ABCMeta, abstractmethod
from logging import getLogger
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from logging import Logger
    from typing import Self

logger: Logger = getLogger(__name__)


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
                f"A {__name__} method of the {self.__class__.__name__} "
                f"interface must be implemented"
            )
        )
