from __future__ import annotations

from abc import ABCMeta, abstractmethod
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from smtplib import SMTP
    from typing import Self


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
        raise NotImplementedError(
            (
                f"A `{__name__}` method of the `{self.__class__.__name__}` "
                f"interface must be implemented"
            )
        )
