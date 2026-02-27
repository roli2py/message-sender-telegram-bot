from __future__ import annotations

from abc import ABCMeta, abstractmethod
from logging import getLogger
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from logging import Logger
    from typing import Self

logger: Logger = getLogger(__name__)


class Authorization(metaclass=ABCMeta):
    """An autorization interface."""

    @abstractmethod
    def authorize(self: Self) -> bool:
        """
        Initializes an authorization.

        :return: A success of the authorization.
        :rtype: bool
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
