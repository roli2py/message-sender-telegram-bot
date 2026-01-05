from __future__ import annotations

from smtplib import SMTP
from typing import TYPE_CHECKING, Self, final, override

from .sender import Sender

if TYPE_CHECKING:
    from typing import Self


@final
class EmailSender(Sender):

    def __init__(self: Self, smtp: SMTP, from_addr: str, to_addr: str) -> None:
        self.__smtp: SMTP = smtp
        self.__from_addr: str = from_addr
        self.__to_addr: str = to_addr

    @override
    def send(self: Self, data: str) -> None:
        _ = self.__smtp.sendmail(
            self.__from_addr,
            self.__to_addr,
            data.encode(),
        )
