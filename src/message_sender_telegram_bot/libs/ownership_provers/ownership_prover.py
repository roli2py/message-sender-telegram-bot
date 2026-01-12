from abc import ABCMeta, abstractmethod
from logging import getLogger
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from logging import Logger
    from typing import Self

logger: Logger = getLogger(__name__)


class OwnershipProver(metaclass=ABCMeta):
    """An ownership prover interface."""

    @abstractmethod
    def prove(self: Self) -> bool:
        """
        Proves an ownership.

        :return: A ownership status.
        :rtype: bool
        :raises NotImplementedError: Must be implemented.
        """
        logger.critical(
            (
                f"A `%s` method of the `%s` interface is invoked. Raising a "
                f"`NotImplementedError` exception..."
            ),
            __name__,
            self.__class__.__name__,
            exc_info=True,
        )
        raise NotImplementedError(
            (
                f"The `{__name__}` method of the `{self.__class__.__name__}` "
                f"interface must be implemented"
            )
        )
