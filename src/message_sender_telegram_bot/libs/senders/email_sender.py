from __future__ import annotations

from logging import getLogger
from smtplib import SMTP
from typing import TYPE_CHECKING, Self, override

from .sender import Sender

if TYPE_CHECKING:
    from logging import Logger
    from typing import Self

logger: Logger = getLogger(__name__)


class EmailSender(Sender):
    """
    A email sender.

    :param Sender: A sender interface.
    :type Sender: class
    """

    def __init__(self: Self, smtp: SMTP, from_addr: str, to_addr: str) -> None:
        """
        Creates an email sender.

        :param smtp: An SMTP object.
        :type smtp: SMTP
        :param from_addr: A "From:" email address.
        :type from_addr: str
        :param to_addr: A "To:" email address.
        :type to_addr: str
        """
        logger.debug("Initializing `%s`...", self.__class__.__name__)

        logger.debug(
            "Setting the arguments to the corresponding instance attributes..."
        )
        self.__smtp: SMTP = smtp
        self.__from_addr: str = from_addr
        self.__to_addr: str = to_addr
        logger.debug("Set")

        logger.debug("Initialized")

    @override
    def send(self: Self, data: str) -> None:
        """
        Sends an email.

        :param data: Data to send.
        :type data: str
        """
        logger.debug("Starting a sending of the data by an email...")

        logger.debug("Sending the data by an email...")
        _ = self.__smtp.sendmail(
            self.__from_addr,
            self.__to_addr,
            data.encode(),
        )
        logger.debug("Sent")
