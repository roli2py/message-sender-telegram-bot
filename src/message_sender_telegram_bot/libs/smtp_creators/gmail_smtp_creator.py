from __future__ import annotations

from logging import error
from smtplib import (
    SMTP_SSL,
    SMTPAuthenticationError,
    SMTPException,
    SMTPHeloError,
    SMTPNotSupportedError,
)
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

        try:
            _ = smtp.login(self.__login, self.__password)
        except (
            SMTPAuthenticationError,
            SMTPException,
            SMTPHeloError,
            SMTPNotSupportedError,
        ):
            # TODO think about the handle of the errors
            error("Failed to log in in the SMTP server")

        return smtp
