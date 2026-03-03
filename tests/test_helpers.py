from datetime import datetime, timedelta
from typing import Self
from unittest.mock import MagicMock, patch
from uuid import UUID

import pytest
from sqlalchemy.orm import Session, sessionmaker
from telegram import Chat, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.constants import ChatType

from message_sender_telegram_bot.libs import (
    EmailSender,
    GmailSMTPCreator,
    Helpers,
    User,
)
from message_sender_telegram_bot.libs.consts import Answers, ButtonTexts


@pytest.fixture(scope="function")
@patch("sqlalchemy.orm.sessionmaker", autospec=True)
def helpers(compiled_session_mock: sessionmaker[Session]) -> Helpers:
    gmail_smtp_login = "GMAIL_SMTP_LOGIN"
    gmail_smtp_password = "GMAIL_SMTP_PASSWORD"
    email_from_addr = "EMAIL_FROM_ADDR"
    email_to_addr = "EMAIL_TO_ADDR"

    return Helpers(
        gmail_smtp_login,
        gmail_smtp_password,
        email_from_addr,
        email_to_addr,
        compiled_session_mock,
    )


@pytest.fixture(scope="function")
@patch("telegram.Chat", autospec=True)
def chat_mock(chat_class_mock: type[Chat]) -> Chat:
    chat_id = 194657302
    return chat_class_mock(chat_id, ChatType.PRIVATE)


@pytest.fixture(scope="function")
def message_text() -> str:
    return "Hello, World!"


@pytest.fixture(scope="function")
@patch(
    "message_sender_telegram_bot.libs.rdb.database_tables.User",
    autospec=True,
)
def db_user_mock(db_user_class_mock: type[User]) -> User:
    id_ = UUID("2050c8a2-2dd3-4801-a56f-bc6cf7d5e59e")
    user_id = 6573920184
    db_user_mock = db_user_class_mock(
        id_,
        user_id,
        is_authorizing=False,
        token_id=None,
        valid_token=None,
        is_owner=False,
        # The fixture will assign `last_send_date` later
        last_send_date=None,
        messages=[],
    )
    # Patched `__init__` can't assign a `datetime` object. So, the
    # fixture assigns a `datetime` by an attribute
    db_user_mock.last_send_date = datetime(2026, 3, 3, 15, 41, 25)
    return db_user_mock


class TestAuthorize:
    @pytest.mark.asyncio
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
        helpers: Helpers,
        chat_mock: Chat,
        message_text: str,
        db_user_mock: User,
    ) -> None:
        await helpers.authorize(chat_mock, message_text, db_user_mock)

        chat_mock.send_message.assert_called_once_with(  # type: ignore[unresolved-attribute]
            Answers.TOKEN_IS_NOT_VALID,
        )

    @pytest.mark.asyncio
    async def test_success_authorization(
        self: Self,
        helpers: Helpers,
        chat_mock: Chat,
        message_text: str,
        db_user_mock: User,
    ) -> None:
        await helpers.authorize(chat_mock, message_text, db_user_mock)

        chat_mock.send_message.assert_called_once_with(Answers.AUTHORIZED)  # type:ignore[unresolved-attribute]


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


class TestShowMessageConfirmationPanel:
    @pytest.mark.asyncio
    @patch("telegram.Chat", autospec=True)
    async def test_send_of_confirmation_panel_with_message(
        self: Self,
        helpers: Helpers,
        chat_mock: Chat,
    ) -> None:
        message_id = 923840239
        yes_button = InlineKeyboardButton(
            ButtonTexts.YES,
            callback_data=f"message_confirmation,true,{message_id}",
        )
        no_button = InlineKeyboardButton(
            ButtonTexts.NO,
            callback_data=f"message_confirmation,false,{message_id}",
        )
        reply_markup = InlineKeyboardMarkup([[yes_button, no_button]])

        await helpers.show_message_confirmation_panel(chat_mock, message_id)

        chat_mock.send_message.assert_called_once_with(  # type: ignore[unresolved-attribute]
            Answers.SEND_MESSAGE_QUESTION,
            reply_markup=reply_markup,
        )


class TestCheckCooldown:
    @pytest.mark.asyncio
    async def test_pass_when_last_send_date_is_missing(
        self: Self,
        helpers: Helpers,
        db_user_mock: User,
    ):
        db_user_mock.last_send_date = None

        is_cooldown_passed, remained_time = await helpers.check_cooldown(
            db_user_mock,
        )

        assert isinstance(is_cooldown_passed, bool)
        assert is_cooldown_passed

        assert isinstance(remained_time, timedelta)
        assert remained_time == timedelta()

    @pytest.mark.asyncio
    @patch(
        (
            "message_sender_telegram_bot.libs.cooldown_checkers."
            "message_send_cooldown_checker.datetime"
        ),
        autospec=True,
        now=MagicMock(return_value=datetime(2026, 3, 3, 15, 41, 30)),
    )
    @patch(
        ("message_sender_telegram_bot.libs.helpers.datetime"),
        autospec=True,
        now=MagicMock(return_value=datetime(2026, 3, 3, 15, 41, 30)),
    )
    async def test_reject_of_pass_when_cooldown_is_not_passed(
        self: Self,
        # Patches of `datetime` gives a mock to args, but the test
        # doesn't need it
        helpers_datetime_mock: type[datetime],
        checker_datetime_mock: type[datetime],
        helpers: Helpers,
        db_user_mock: User,
    ) -> None:
        is_cooldown_passed, remained_time = await helpers.check_cooldown(
            db_user_mock,
        )

        assert isinstance(is_cooldown_passed, bool)
        assert not is_cooldown_passed

        assert isinstance(remained_time, timedelta)
        assert remained_time == timedelta(seconds=25)

    @pytest.mark.asyncio
    @patch(
        (
            "message_sender_telegram_bot.libs.cooldown_checkers."
            "message_send_cooldown_checker.datetime"
        ),
        autospec=True,
        now=MagicMock(return_value=datetime(2026, 3, 3, 15, 41, 56)),
    )
    @patch(
        ("message_sender_telegram_bot.libs.helpers.datetime"),
        autospec=True,
        now=MagicMock(return_value=datetime(2026, 3, 3, 15, 41, 56)),
    )
    async def test_pass_when_cooldown_is_passed(
        self: Self,
        # Patches of `datetime` gives a mock to args, but the test
        # doesn't need it
        helpers_datetime_mock: type[datetime],
        checker_datetime_mock: type[datetime],
        helpers: Helpers,
        db_user_mock: User,
    ) -> None:
        is_cooldown_passed, remained_time = await helpers.check_cooldown(
            db_user_mock,
        )

        assert isinstance(is_cooldown_passed, bool)
        assert is_cooldown_passed

        assert isinstance(remained_time, timedelta)
        assert remained_time == timedelta()
