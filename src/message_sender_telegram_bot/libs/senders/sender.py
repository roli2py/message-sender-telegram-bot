from __future__ import annotations

from abc import ABCMeta, abstractmethod
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from typing import Self


class Sender(metaclass=ABCMeta):

    @abstractmethod
    def send(self: Self, data: str) -> None:
        raise NotImplementedError(
            f"The `send` method of the `Sender` interface must be implemented"
        )
