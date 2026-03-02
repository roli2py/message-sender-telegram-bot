from typing import Self
from unittest.mock import MagicMock, patch

import pytest
from sqlalchemy.orm import Session, sessionmaker
from telegram import Chat

from message_sender_telegram_bot.libs import (
    EmailSender,
    GmailSMTPCreator,
    Helpers,
)
from message_sender_telegram_bot.libs.consts import Answers
from message_sender_telegram_bot.libs.rdb import database_tables


@pytest.fixture
@patch("sqlalchemy.orm.sessionmaker", autospec=True)
def helpers(sessionmaker_mock: sessionmaker) -> Helpers:
    gmail_smtp_login = "GMAIL_SMTP_LOGIN"
    gmail_smtp_password = "GMAIL_SMTP_PASSWORD"
    email_from_addr = "EMAIL_FROM_ADDR"
    email_to_addr = "EMAIL_TO_ADDR"

    compiled_session_mock: sessionmaker[Session] = sessionmaker_mock()

    return Helpers(
        gmail_smtp_login,
        gmail_smtp_password,
        email_from_addr,
        email_to_addr,
        compiled_session_mock,
    )


class TestAuthorize:
    @pytest.mark.asyncio
    @patch(
        "message_sender_telegram_bot.libs.rdb.database_tables",
        autospec=True,
    )
    @patch("telegram.Chat", autospec=True)
    @patch(
        "message_sender_telegram_bot.libs.helpers.DBValidTokenManipulator",
        autospec=True,
        return_value=MagicMock(get=MagicMock(return_value=None)),
    )
    async def test_detect_of_invalid_token(
        # Patch of `DBValidTokenManipulator` gives a mock to args, but
        # the test doesn't need it
        self: Self,
        _,
        chat_mock: Chat,
        db_user_mock: database_tables.User,
        helpers: Helpers,
    ) -> None:
        message_text = "MESSAGE_TEXT"

        await helpers.authorize(chat_mock, message_text, db_user_mock)

        chat_mock.send_message.assert_called_once_with(  # type: ignore[unresolved-attribute]
            Answers.TOKEN_IS_NOT_VALID,
        )


class TestSendEmail:
    @pytest.mark.asyncio
    @patch(
        "message_sender_telegram_bot.libs.helpers.EmailSender",
        autospec=True,
    )
    @patch(
        "message_sender_telegram_bot.libs.helpers.GmailSMTPCreator",
        autospec=True,
    )
    async def test_send_of_email(
        self: Self,
        gmail_smtp_creator_mock: GmailSMTPCreator,
        email_sender_mock: EmailSender,
        helpers: Helpers,
    ) -> None:
        name = "NAME"
        text = "TEXT"

        await helpers.send_email(name, text)

        email_sender_mock.return_value.send.assert_called_once_with(text)  # type: ignore[unresolved-attribute]
