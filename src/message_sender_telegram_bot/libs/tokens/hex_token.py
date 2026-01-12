from __future__ import annotations

from logging import getLogger
from re import search
from typing import TYPE_CHECKING, override

from .token import Token

if TYPE_CHECKING:
    from logging import Logger
    from typing import Self

logger: Logger = getLogger(__name__)


class HexToken(Token):
    """
    A hex token.

    :param Token: A token interface.
    :type Token: class
    """

    def __init__(self: Self, token: str) -> None:
        """
        Creates a hex token.

        :param token: A supposed token.
        :type token: str
        :raises ValueError: A token contains not-compitable symbols.
        """
        logger.debug("Initializing `%s`...", self.__class__.__name__)

        logger.debug("Verifying a token to not-compitable symbols...")
        if search(r"[^0-9a-fA-F]", token) is not None:
            logger.critical(
                (
                    "The token contains not-compitable symbols. Raising a "
                    "`ValueError` exception..."
                )
            )
            raise ValueError(
                "A provided token contains not-compitable symbols"
            )

        logger.debug(
            "Setting the arguments to the corresponding instance attributes..."
        )
        self.__token: str = token
        logger.debug("Set")

        logger.debug("Initialized")

    @override
    def __str__(self: Self) -> str:
        return self.get()

    @override
    def get(self: Self) -> str:
        """
        Returns a hex token.

        :return: A hex token.
        :rtype: str
        """
        logger.debug("Starting a getting of the hex token...")

        logger.debug("Getting the hex token...")
        hex_token: str = self.__token
        logger.debug("Got")

        return hex_token
