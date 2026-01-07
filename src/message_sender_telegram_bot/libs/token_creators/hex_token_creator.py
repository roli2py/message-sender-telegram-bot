from __future__ import annotations

from secrets import token_hex
from typing import TYPE_CHECKING, override

from ..tokens import HexToken
from .token_creator import TokenCreator

if TYPE_CHECKING:
    from typing import Self

    from ..tokens import Token


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
        return HexToken(token_hex())
