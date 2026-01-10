from __future__ import annotations

from typing import TYPE_CHECKING, final, override

from ..tokens import Token
from .authorization import Authorization

if TYPE_CHECKING:
    from typing import Self


@final
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
        self.__valid_tokens = valid_tokens
        self.__token = token

    @override
    def authorize(self: Self) -> bool:
        """
        Initializes an authorization.

        :return: A success of the authorization.
        :rtype: bool
        """
        return self.__token in self.__valid_tokens
