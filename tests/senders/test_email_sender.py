from collections.abc import Generator
from smtplib import SMTP
from typing import Literal, cast

import pytest
from pytest_mock import MockerFixture

from message_sender_telegram_bot.libs import EmailSender


@pytest.fixture
def smtp_mock(mocker: MockerFixture) -> Generator[SMTP]:
    smtp_mock = cast(SMTP, mocker.patch("smtplib.SMTP", autospec=True))
    yield smtp_mock
    del smtp_mock


@pytest.fixture
def from_addr() -> str:
    return "mail1@example.com"


@pytest.fixture
def to_addr() -> str:
    return "mail2@example.com"


def test_choose_of_anonymous_sender_name_in_contructor(
    smtp_mock: SMTP,
    from_addr: str,
    to_addr: str,
) -> None:
    email_sender: EmailSender = EmailSender(smtp_mock, from_addr, to_addr)
    sender_name: str = email_sender.sender_name

    assert isinstance(sender_name, str)
    assert sender_name == "Anonymous"


def test_choose_of_provided_sender_name_in_contructor(
    smtp_mock: SMTP,
    from_addr: str,
    to_addr: str,
) -> None:
    provided_sender_name = "John"

    email_sender: EmailSender = EmailSender(
        smtp_mock,
        from_addr,
        to_addr,
        sender_name=provided_sender_name,
    )
    sender_name: str = email_sender.sender_name

    assert isinstance(sender_name, str)
    assert sender_name == provided_sender_name


@pytest.fixture
def email_sender(smtp_mock: SMTP) -> EmailSender:
    return EmailSender(
        smtp_mock,
        "mail1@example.com",
        "mail2@example.com",
        sender_name="John",
    )


def test_set_of_sender_name_of_email_sender(
    email_sender: EmailSender,
) -> None:
    previous_receiver_sender_name: str = email_sender.sender_name
    new_sender_name: str = "Mike"

    email_sender.sender_name: Literal["Mike"] = new_sender_name
    new_received_sender_name: str = email_sender.sender_name

    assert previous_receiver_sender_name != new_received_sender_name
    assert new_received_sender_name == new_sender_name


def test_send_ascii_text(email_sender: EmailSender) -> None:
    email_sender.send("Hello, World!")


def test_send_not_ascii_text(email_sender: EmailSender) -> None:
    email_sender.send("Привет, Мир!")
