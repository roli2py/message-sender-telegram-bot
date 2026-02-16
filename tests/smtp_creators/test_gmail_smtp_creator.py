from smtplib import SMTP, SMTP_SSL, SMTPAuthenticationError
from unittest.mock import MagicMock, patch

from pytest import fixture, raises

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


@fixture
def gmail_smtp_creator() -> GmailSMTPCreator:
    return GmailSMTPCreator(
        CORRECT_SMTP_TEST_LOGIN, CORRECT_SMTP_TEST_PASSWORD
    )


@fixture
def gmail_smtp_creator_with_bad_credentials() -> GmailSMTPCreator:
    return GmailSMTPCreator(BAD_SMTP_TEST_LOGIN, BAD_SMTP_TEST_PASSWORD)


@patch(
    (
        "message_sender_telegram_bot.libs.smtp_creators.gmail_smtp_creator."
        "SMTP_SSL"
    ),
    return_value=MagicMock(
        spec=SMTP_SSL,
        login=login_func_mock,
    ),
)
def test_smtp_creation(_, gmail_smtp_creator: GmailSMTPCreator) -> None:
    smtp: SMTP = gmail_smtp_creator.create()

    assert isinstance(smtp, SMTP)


@patch(
    (
        "message_sender_telegram_bot.libs.smtp_creators.gmail_smtp_creator."
        "SMTP_SSL"
    ),
    return_value=MagicMock(
        spec=SMTP_SSL,
        login=login_func_mock,
    ),
)
def test_smtp_creation_with_bad_credentials(
    _,
    gmail_smtp_creator_with_bad_credentials: GmailSMTPCreator,
) -> None:
    with raises(SMTPAuthenticationError):
        _ = gmail_smtp_creator_with_bad_credentials.create()
