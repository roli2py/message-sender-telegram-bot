from __future__ import annotations

from logging import getLogger
from textwrap import dedent
from typing import TYPE_CHECKING, override

from ..interfaces import Sender

if TYPE_CHECKING:
    from logging import Logger
    from smtplib import SMTP
    from typing import Self

logger: Logger = getLogger(__name__)


class EmailSender(Sender):
    """
    A email sender.

    :param Sender: A sender interface.
    :type Sender: class
    """

    def __init__(
        self: Self,
        smtp: SMTP,
        from_addr: str,
        to_addr: str,
        *,
        sender_name: str | None = None,
    ) -> None:
        """
        Creates an email sender.

        :param smtp: An SMTP object.
        :type smtp: SMTP
        :param from_addr: A "From:" email address.
        :type from_addr: str
        :param to_addr: A "To:" email address.
        :type to_addr: str
        :param sender_name: A sender name, defaults to None.
        :type sender_name: str | None, optional
        """
        logger.debug("Initializing `%s`...", self.__class__.__name__)

        logger.debug("Checking a presence of a sender name...")
        if sender_name is not None:
            logger.debug(
                'The sender name is provided. Choosing the "%s" name',
                sender_name,
            )
            chosen_sender_name: str = sender_name
        else:
            logger.debug(
                (
                    "The sender name is not provided. Choosing the "
                    '"Anonymous" name'
                )
            )
            chosen_sender_name = "Anonymous"

        logger.debug(
            "Setting the arguments to the corresponding instance attributes..."
        )
        self.__smtp: SMTP = smtp
        self.__from_addr: str = from_addr
        self.__to_addr: str = to_addr
        self.__sender_name: str = chosen_sender_name
        logger.debug("Set")

        logger.debug("Initialized")

    @property
    def sender_name(self: Self) -> str:
        """
        Gets a sender name.

        :return: A sender name.
        :rtype: str
        """
        return self.__sender_name

    @sender_name.setter
    def sender_name(self: Self, sender_name: str) -> None:
        """
        Sets a sender name.

        :param sender_name: A sender name to set.
        :type sender_name: str
        """
        self.__sender_name: str = sender_name

    @override
    def send(self: Self, data: str) -> None:
        """
        Sends an email.

        :param data: Data to send.
        :type data: str
        """
        logger.debug("Starting a sending of the data by an email...")

        logger.debug("Constructing a message...")
        message: bytes = (
            dedent(
                """
                Subject: A message from Telegram

                {data}

                — {sender_name}
                """
            )
            .strip()
            .format(data=data, sender_name=self.__sender_name)
            .encode()
        )
        logger.debug("Constructed")

        logger.debug("Sending the data by an email...")
        _ = self.__smtp.sendmail(
            self.__from_addr,
            self.__to_addr,
            message,
        )
        logger.debug("Sent")
