from __future__ import annotations

from logging import getLogger
from secrets import token_hex
from typing import TYPE_CHECKING, override

from ..tokens import HexToken
from .token_creator import TokenCreator

if TYPE_CHECKING:
    from logging import Logger
    from typing import Self

    from ..tokens import Token

logger: Logger = getLogger(__name__)


class HexTokenCreator(TokenCreator):
    """
    A hex token creator.

    :param TokenCreator: A token creator interface.
    :type TokenCreator: class
    """

    @override
    def create(self: Self) -> Token:
        """
        Creates a hex token.

        :raises NotImplementedError: Must to be implemented
        :return: A hex token.
        :rtype: Token
        """
        logger.debug("Starting a creation of a new hex token...")

        logger.debug("Creating a new hex token...")
        hex_token: HexToken = HexToken(token_hex())
        logger.debug("Created")

        return hex_token
