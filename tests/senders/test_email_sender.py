from smtplib import SMTP
from typing import Literal
from unittest.mock import patch

from pytest import fixture

from message_sender_telegram_bot.libs import EmailSender


@fixture
@patch("smtplib.SMTP")
def smtp(smtp_mock: SMTP) -> SMTP:
    return smtp_mock


@fixture
def from_addr() -> str:
    return "mail1@example.com"


@fixture
def to_addr() -> str:
    return "mail2@example.com"


def test_a_choose_of_an_anonymous_sender_name_in_the_contructor(
    smtp: SMTP,
    from_addr: str,
    to_addr: str,
) -> None:
    email_sender: EmailSender = EmailSender(smtp, from_addr, to_addr)
    sender_name: str = email_sender.sender_name

    assert isinstance(sender_name, str)
    assert sender_name == "Anonymous"


def test_a_choose_of_an_provided_sender_name_in_the_contructor(
    smtp: SMTP,
    from_addr: str,
    to_addr: str,
) -> None:
    provided_sender_name = "John"

    email_sender: EmailSender = EmailSender(
        smtp, from_addr, to_addr, sender_name=provided_sender_name
    )
    sender_name: str = email_sender.sender_name

    assert isinstance(sender_name, str)
    assert sender_name == provided_sender_name


@fixture
def email_sender(smtp: SMTP) -> EmailSender:
    return EmailSender(
        smtp,
        "mail1@example.com",
        "mail2@example.com",
        sender_name="John",
    )


def test_set_of_sender_name_of_the_email_sender(
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
