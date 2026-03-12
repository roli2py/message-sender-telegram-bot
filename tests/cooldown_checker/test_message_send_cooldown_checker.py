from datetime import datetime, timedelta
from unittest.mock import MagicMock

from pytest import fixture, raises
from pytest_mock import MockerFixture

from message_sender_telegram_bot.libs import MessageSendCooldownChecker

datetime_in_cooldown_period: datetime = datetime.fromisoformat(
    "2026-01-13T14:30:30Z"
)
datetime_out_of_cooldown_period: datetime = datetime.fromisoformat(
    "2026-01-13T14:31:00Z"
)


@fixture
def last_send_date() -> datetime:
    return datetime.fromisoformat("2026-01-13T14:30:25Z")


@fixture
def cooldown() -> timedelta:
    return timedelta(seconds=30)


@fixture
def pass_date() -> datetime:
    return datetime.fromisoformat("2026-01-13T14:30:55Z")


def test_reject_of_init_without_cooldown_and_pass_date(
    last_send_date: datetime,
) -> None:
    with raises(
        ValueError,
        match="A cooldown or a pass date must be provided",
    ):
        MessageSendCooldownChecker(last_send_date)  # type: ignore


def test_reject_of_init_with_cooldown_and_pass_date(
    last_send_date: datetime,
    cooldown: timedelta,
    pass_date: datetime,
) -> None:
    with raises(
        ValueError,
        match="Only a cooldown or a pass date must be provided",
    ):
        MessageSendCooldownChecker(
            last_send_date,
            cooldown=cooldown,
            pass_date=pass_date,
        )  # type: ignore


@fixture
def message_send_cooldown_checker_with_cooldown(
    last_send_date: datetime,
    cooldown: timedelta,
) -> MessageSendCooldownChecker:
    return MessageSendCooldownChecker(last_send_date, cooldown=cooldown)


@fixture
def message_send_cooldown_checker_with_pass_date(
    last_send_date: datetime,
    pass_date: datetime,
) -> MessageSendCooldownChecker:
    return MessageSendCooldownChecker(last_send_date, pass_date=pass_date)


def test_is_pass_method_with_cooldown_in_cooldown_period(
    mocker: MockerFixture,
    message_send_cooldown_checker_with_cooldown: MessageSendCooldownChecker,
) -> None:
    mocker.patch(
        (
            "message_sender_telegram_bot.libs.cooldown_checkers."
            "message_send_cooldown_checker.datetime"
        ),
        autospec=True,
        now=MagicMock(return_value=datetime_in_cooldown_period),
    )
    is_cooldown_pass: bool = (
        message_send_cooldown_checker_with_cooldown.is_passed()
    )

    assert isinstance(is_cooldown_pass, bool)
    assert not is_cooldown_pass


def test_is_pass_method_with_pass_date_in_cooldown_period(
    mocker: MockerFixture,
    message_send_cooldown_checker_with_pass_date: MessageSendCooldownChecker,
) -> None:
    mocker.patch(
        (
            "message_sender_telegram_bot.libs.cooldown_checkers."
            "message_send_cooldown_checker.datetime"
        ),
        autospec=True,
        now=MagicMock(return_value=datetime_in_cooldown_period),
    )
    is_cooldown_pass: bool = (
        message_send_cooldown_checker_with_pass_date.is_passed()
    )

    assert isinstance(is_cooldown_pass, bool)
    assert not is_cooldown_pass


def test_is_pass_method_with_cooldown_out_of_cooldown_period(
    mocker: MockerFixture,
    message_send_cooldown_checker_with_cooldown: MessageSendCooldownChecker,
) -> None:
    mocker.patch(
        (
            "message_sender_telegram_bot.libs.cooldown_checkers."
            "message_send_cooldown_checker.datetime"
        ),
        autospec=True,
        now=MagicMock(return_value=datetime_out_of_cooldown_period),
    )
    is_cooldown_pass: bool = (
        message_send_cooldown_checker_with_cooldown.is_passed()
    )

    assert isinstance(is_cooldown_pass, bool)
    assert is_cooldown_pass


def test_is_pass_method_with_pass_date_out_of_cooldown_period(
    mocker: MockerFixture,
    message_send_cooldown_checker_with_pass_date: MessageSendCooldownChecker,
) -> None:
    mocker.patch(
        (
            "message_sender_telegram_bot.libs.cooldown_checkers."
            "message_send_cooldown_checker.datetime"
        ),
        autospec=True,
        now=MagicMock(return_value=datetime_out_of_cooldown_period),
    )
    is_cooldown_pass: bool = (
        message_send_cooldown_checker_with_pass_date.is_passed()
    )

    assert isinstance(is_cooldown_pass, bool)
    assert is_cooldown_pass
