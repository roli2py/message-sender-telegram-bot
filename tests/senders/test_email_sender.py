from smtplib import SMTP
from unittest.mock import patch

from pytest import fixture

from libs import EmailSender


@fixture
@patch("smtplib.SMTP")
def smtp(smtp_mock: SMTP) -> SMTP:
    return smtp_mock


@fixture
def email_sender(smtp: SMTP) -> EmailSender:
    return EmailSender(smtp, "mail1@example.com", "mail2@example.com")


def test_send_ascii_text(email_sender: EmailSender) -> None:
    email_sender.send("Hello, World!")


def test_send_not_ascii_text(email_sender: EmailSender) -> None:
    email_sender.send("Привет, Мир!")
