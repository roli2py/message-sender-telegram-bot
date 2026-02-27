from __future__ import annotations

from logging import getLogger
from typing import TYPE_CHECKING, override

from ..interfaces.authorization import Authorization
from ..types import Token

if TYPE_CHECKING:
    from logging import Logger
    from typing import Self

logger: Logger = getLogger(__name__)


class TokenAuthorization(Authorization):
    """
    An authorization by a token.

    :param Authorization: An authorization interface.
    :type Authorization: class
    """

    def __init__[TokenType: Token](
        self: Self, valid_tokens: set[TokenType], token: TokenType
    ) -> None:
        """
        Creates a token authorization.
        """
        logger.debug("Initializing `%s`...", self.__class__.__name__)

        logger.debug(
            "Setting the arguments to the corresponding instance attributes..."
        )
        self.__valid_tokens = valid_tokens
        self.__token = token
        logger.debug("Set")

        logger.debug("Initialized")

    @override
    def authorize(self: Self) -> bool:
        """
        Initializes an authorization.

        :return: A success of the authorization.
        :rtype: bool
        """
        logger.debug("Starting an authorizing by a hex token...")

        logger.debug("Authorizing...")
        is_authorizing_success: bool = self.__token in self.__valid_tokens

        if is_authorizing_success:
            logger.debug("Authorized")
        else:
            logger.debug("Authorizing is not success")

        return is_authorizing_success
