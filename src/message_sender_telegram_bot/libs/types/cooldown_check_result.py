from __future__ import annotations

from typing import TYPE_CHECKING, NamedTuple

if TYPE_CHECKING:
    from datetime import timedelta


class CooldownCheckResult(NamedTuple):
    is_cooldown_pass: bool
    remained_time: timedelta
