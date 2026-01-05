from __future__ import annotations

from abc import ABCMeta, abstractmethod
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from smtplib import SMTP
    from typing import Self


class SMTPCreator(metaclass=ABCMeta):

    @abstractmethod
    def create(self: Self) -> SMTP:
        raise NotImplementedError(
            (
                f"A `{__name__}` method of the `{self.__class__.__name__}` "
                "interface must be implemented"
            )
        )
