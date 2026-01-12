from __future__ import annotations

from logging import getLogger
from smtplib import SMTP_SSL
from typing import TYPE_CHECKING, override

from .smtp_creator import SMTPCreator

if TYPE_CHECKING:
    from logging import Logger
    from smtplib import SMTP
    from typing import Self

logger: Logger = getLogger(__name__)


class GmailSMTPCreator(SMTPCreator):
    """
    A SMTP creator for gmail.

    :param SMTPCreator: A SMTP creator interface.
    :type SMTPCreator: class
    """

    # TODO move to the constants
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
        logger.debug("Initializing `%s`...", self.__class__.__name__)

        logger.debug(
            "Setting the arguments to the corresponding instance attributes..."
        )
        self.__login: str = login
        self.__password: str = password
        logger.debug("Set")

        logger.debug("Initialized")

    @override
    def create(self: Self) -> SMTP:
        """
        Creates an SMTP instance connected to gmail.

        :return: A SMTP instance connected to gmail.
        :rtype: SMTP
        """
        logger.debug("Starting a creation of a SMTP instance...")

        logger.debug("Creating a SMTP instance...")
        smtp: SMTP_SSL = SMTP_SSL(host=self.__host, port=self.__port)
        logger.debug("Created")

        logger.debug("Logging in to the gmail SMTP server...")
        _ = smtp.login(self.__login, self.__password)
        logger.debug("Logged in")

        return smtp
