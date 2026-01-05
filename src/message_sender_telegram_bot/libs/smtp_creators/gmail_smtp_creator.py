from __future__ import annotations

from smtplib import SMTP_SSL
from typing import TYPE_CHECKING, final, override

from .smtp_creator import SMTPCreator

if TYPE_CHECKING:
    from smtplib import SMTP
    from typing import Self


@final
class GmailSMTPCreator(SMTPCreator):
    __host: str = "smtp.gmail.com"
    __port: int = 465

    def __init__(self: Self, login: str, password: str) -> None:
        self.__login: str = login
        self.__password: str = password

    @override
    def create(self: Self) -> SMTP:
        smtp: SMTP_SSL = SMTP_SSL(host=self.__host, port=self.__port)

        _ = smtp.login(self.__login, self.__password)

        return smtp
