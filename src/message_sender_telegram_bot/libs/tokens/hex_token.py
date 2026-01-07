from __future__ import annotations

from re import search
from typing import TYPE_CHECKING, override

from .token import Token

if TYPE_CHECKING:
    from typing import Self


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
        :raises ValueError: A token contains not-compitable symbols
        """
        if search(r"[^0-9a-fA-F]", token) is not None:
            raise ValueError(
                "A provided token contains not-compitable symbols"
            )

        self.__token: str = token

    @override
    def get(self: Self) -> str:
        """
        Returns a hex token.

        :return: A hex token.
        :rtype: str
        """
        return self.__token
