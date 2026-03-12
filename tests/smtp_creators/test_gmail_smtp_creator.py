from collections.abc import Generator
from smtplib import SMTP, SMTP_SSL, SMTPAuthenticationError
from unittest.mock import MagicMock

import pytest
from pytest_mock import MockerFixture

from message_sender_telegram_bot.libs import GmailSMTPCreator

CORRECT_SMTP_TEST_LOGIN = "SMTP_LOGIN"
CORRECT_SMTP_TEST_PASSWORD = "SMTP_PASSWORD"
BAD_SMTP_TEST_LOGIN = "BAD_SMTP_LOGIN"
BAD_SMTP_TEST_PASSWORD = "BAD_SMTP_PASSWORD"


def login_func_mock(
    login: str, password: str, *, _: bool = True
) -> tuple[int, bytes]:
    if (
        login == CORRECT_SMTP_TEST_LOGIN
        and password == CORRECT_SMTP_TEST_PASSWORD
    ):
        return (235, b"2.7.0 Accepted")
    else:
        raise SMTPAuthenticationError(
            535,
            (
                b"5.7.8 Username and Password not accepted. For more "
                b"information, go to\n5.7.8  "
                b"https://support.google.com/mail/?p=BadCredentials "
                b"123456789000-1234567891234567890000.12 - gsmtp"
            ),
        )


@pytest.fixture
def gmail_smtp_creator() -> GmailSMTPCreator:
    return GmailSMTPCreator(
        CORRECT_SMTP_TEST_LOGIN, CORRECT_SMTP_TEST_PASSWORD
    )


@pytest.fixture
def gmail_smtp_creator_with_bad_credentials() -> GmailSMTPCreator:
    return GmailSMTPCreator(BAD_SMTP_TEST_LOGIN, BAD_SMTP_TEST_PASSWORD)


@pytest.fixture
def smtp_ssl_mock(mocker: MockerFixture) -> Generator[SMTP_SSL]:
    smtp_ssl_class_mock = mocker.patch(
        (
            "message_sender_telegram_bot.libs.smtp_creators."
            "gmail_smtp_creator.SMTP_SSL"
        ),
        autospec=True,
        return_value=MagicMock(
            spec=SMTP_SSL,
            login=login_func_mock,
        ),
    )
    smtp_ssl_mock: SMTP_SSL = smtp_ssl_class_mock()
    yield smtp_ssl_mock
    del smtp_ssl_mock


def test_smtp_creation(
    smtp_ssl_mock: SMTP_SSL,
    gmail_smtp_creator: GmailSMTPCreator,
) -> None:

    smtp: SMTP = gmail_smtp_creator.create()

    assert isinstance(smtp, SMTP)


def test_smtp_creation_with_bad_credentials(
    smtp_ssl_mock: SMTP_SSL,
    gmail_smtp_creator_with_bad_credentials: GmailSMTPCreator,
) -> None:
    with pytest.raises(SMTPAuthenticationError):
        _ = gmail_smtp_creator_with_bad_credentials.create()


def test_success_work_of_context_manager(
    smtp_ssl_mock: SMTP_SSL,
    gmail_smtp_creator: GmailSMTPCreator,
) -> None:
    with gmail_smtp_creator as smtp:
        assert isinstance(smtp, SMTP)
