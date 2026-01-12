from __future__ import annotations

from abc import ABCMeta, abstractmethod
from logging import getLogger
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from logging import Logger
    from smtplib import SMTP
    from typing import Self

logger: Logger = getLogger(__name__)


class SMTPCreator(metaclass=ABCMeta):
    """A SMTP creator interface."""

    @abstractmethod
    def create(self: Self) -> SMTP:
        """
        Creates an SMTP instance.

        :return: A SMTP instance.
        :rtype: SMTP
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
                f"A `{__name__}` method of the `{self.__class__.__name__}` "
                f"interface must be implemented"
            )
        )
