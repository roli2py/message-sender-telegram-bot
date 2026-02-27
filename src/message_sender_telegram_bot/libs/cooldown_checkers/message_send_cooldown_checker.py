from __future__ import annotations

from datetime import datetime, timedelta
from logging import getLogger
from typing import TYPE_CHECKING, overload, override

from ..interfaces import CooldownChecker

if TYPE_CHECKING:
    from logging import Logger
    from typing import Self

logger: Logger = getLogger(__name__)


class MessageSendCooldownChecker(CooldownChecker):
    """
    A message send cooldown checker.

    :param CooldownChecker: A cooldown checker interface.
    :type CooldownChecker: class
    """

    @overload
    def __init__(
        self: Self, last_send_date: datetime, *, cooldown: timedelta
    ) -> None: ...

    @overload
    def __init__(
        self: Self, last_send_date: datetime, *, pass_date: datetime
    ) -> None: ...

    def __init__(
        self: Self,
        last_send_date: datetime,
        *,
        cooldown: timedelta | None = None,
        pass_date: datetime | None = None,
    ) -> None:
        """
        Creates a message send cooldown checker.

        :param last_send_date: A date of a last message send.
        :type last_send_date: datetime
        :param cooldown: A cooldown, defaults to None. Either a cooldown
                         or a pass date must be provided but not both.
        :type cooldown: timedelta | None, optional
        :param pass_date: A date when a send access will be returned,
                          defaults to None. Either a cooldown or a pass
                          date must be provided but not both.
        :type pass_date: datetime | None, optional
        """
        logger.debug("Initializing `%s`...", self.__class__.__name__)

        logger.debug(
            (
                "Checking an absent or a presence of the `cooldown` and "
                "`pass_date` arguments..."
            )
        )
        if cooldown is None and pass_date is None:
            logger.critical(
                (
                    "The `cooldown` and `pass_date` arguments is absent. "
                    "Raising a `ValueError` exception..."
                ),
                exc_info=True,
            )
            raise ValueError("A cooldown or a pass date must be provided")
        elif cooldown is not None and pass_date is not None:
            logger.critical(
                (
                    "The `cooldown` and `pass_date` arguments is present. "
                    "Raising a `ValueError` exception..."
                ),
                exc_info=True,
            )
            raise ValueError("Only a cooldown or a pass date must be provided")
        logger.debug(
            (
                "Only a `cooldown` or `pass_date` argument is provided. "
                "Continuing an initializing..."
            )
        )

        logger.debug(
            (
                "Setting the `last_send_date` argument to a `__cooldown` "
                "instance attribute..."
            )
        )
        self.__last_send_date: datetime = last_send_date
        logger.debug("Set")

        logger.debug("Checking a presence of a cooldown argument...")
        if cooldown is not None:
            logger.debug("The argument is present")

            logger.debug("Adding a cooldown to the last send date...")
            self.__pass_date: datetime = self.__last_send_date + cooldown
            logger.debug("Added")
        elif pass_date is not None:
            logger.debug("The argument is absent")

            logger.debug(
                (
                    "Setting the `pass_date` argument to a `__pass_date` "
                    "instance attribute..."
                )
            )
            self.__pass_date = pass_date
            logger.debug("Set")

        logger.debug("Initialized")

    @override
    def is_pass(self: Self) -> bool:
        """
        Checks a pass of the cooldown.

        :return: A pass status of a cooldown.
        :rtype: bool
        """
        logger.debug("Starting a message send cooldown check...")

        logger.debug("Comparing a pass date with current time...")
        pass_status: bool = self.__pass_date < datetime.now()
        logger.debug("Compared")

        return pass_status
