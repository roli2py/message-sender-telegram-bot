from __future__ import annotations

from abc import ABCMeta, abstractmethod
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from typing import Self


class Authorization(metaclass=ABCMeta):
    """An autorization interface."""

    @abstractmethod
    def authorize(self: Self) -> bool:
        """
        Initializes an authorization.

        :return: A success of the authorization.
        :rtype: bool
        :raises NotImplementedError: Must be implemented.
        """
        raise NotImplementedError(
            (
                f"A `{__name__}` method of the `{self.__class__.__name__}` "
                f"interface must be implemented"
            )
        )
