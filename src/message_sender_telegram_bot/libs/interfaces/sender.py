from __future__ import annotations

from abc import ABCMeta, abstractmethod
from logging import getLogger
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from logging import Logger
    from typing import Self

logger: Logger = getLogger(__name__)


class Sender(metaclass=ABCMeta):
    """A sender interface."""

    @abstractmethod
    def send(self: Self, data: str) -> None:
        """
        Sends a data.

        :param data: Data to send.
        :type data: str
        :raises NotImplementedError: Must to be implemented.
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
                f"The `{__name__}` method of the `{self.__class__.__name__}` "
                f"interface must be implemented"
            )
        )
