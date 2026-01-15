from __future__ import annotations

from logging import getLogger
from typing import TYPE_CHECKING, override

from ..db_user_manipulators.abstract_db_user_manipulator import (
    AbstractDBUserManipulator,
)
from .ownership_prover import OwnershipProver

if TYPE_CHECKING:
    from logging import Logger
    from typing import Self

logger: Logger = getLogger(__name__)


class UserOwnershipProver(OwnershipProver):
    """
    A user's ownership prover.

    :param OwnershipProver: An ownership prover interface.
    :type UserOwnershipProver: class
    """

    def __init__(
        self: Self, db_user_manipulator: AbstractDBUserManipulator
    ) -> None:
        """
        Creates a user's ownership prover.

        :param db_user_manipulator: A DB user manipulator. Gets the
                                    owner status.
        :type db_user_manipulator: AbstractDBUserManipulator
        """
        self.__db_user_manipulator: AbstractDBUserManipulator = (
            db_user_manipulator
        )

    @override
    def prove(self: Self) -> bool:
        """
        Proves a user's ownership.

        :return: A user's ownership status.
        :rtype: bool
        """
        is_user_owner: bool = self.__db_user_manipulator.get_owner_status()

        if not is_user_owner:
            return False

        return True
