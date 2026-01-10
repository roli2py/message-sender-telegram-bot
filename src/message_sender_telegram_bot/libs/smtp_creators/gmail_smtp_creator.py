from __future__ import annotations

from smtplib import SMTP_SSL
from typing import TYPE_CHECKING, override

from .smtp_creator import SMTPCreator

if TYPE_CHECKING:
    from smtplib import SMTP
    from typing import Self


class GmailSMTPCreator(SMTPCreator):
    """
    A SMTP creator for gmail.

    :param SMTPCreator: A SMTP creator interface.
    :type SMTPCreator: class
    """

    __host: str = "smtp.gmail.com"
    __port: int = 465

    def __init__(self: Self, login: str, password: str) -> None:
        """
        Creates a gmail SMTP creator.

        :param login: An email that represents a SMTP login for gmail.
        :type login: str
        :param password: An app password that represents a SMTP password
                         for gmail.
        :type password: str
        """
        self.__login: str = login
        self.__password: str = password

    @override
    def create(self: Self) -> SMTP:
        """
        Creates an SMTP instance connected to gmail.

        :return: A SMTP instance connected to gmail.
        :rtype: SMTP
        """
        smtp: SMTP_SSL = SMTP_SSL(host=self.__host, port=self.__port)

        _ = smtp.login(self.__login, self.__password)

        return smtp
