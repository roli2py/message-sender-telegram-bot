from datetime import datetime, timedelta
from smtplib import SMTP
from typing import Generator, Self, cast
from unittest.mock import MagicMock
from uuid import UUID

import pytest
from pytest_mock import MockerFixture
from sqlalchemy.orm import Session, sessionmaker
from telegram import Chat, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.constants import ChatType

from message_sender_telegram_bot.libs import (
    DBUserManipulator,
    EmailSender,
    Helpers,
    User,
)
from message_sender_telegram_bot.libs.consts import Answers, ButtonTexts


@pytest.fixture
def gmail_smtp_login() -> str:
    return "GMAIL_SMTP_LOGIN"


@pytest.fixture
def gmail_smtp_password() -> str:
    return "GMAIL_SMTP_PASSWORD"


@pytest.fixture
def email_from_addr() -> str:
    return "EMAIL_FROM_ADDR"


@pytest.fixture
def email_to_addr() -> str:
    return "EMAIL_TO_ADDR"


@pytest.fixture
def helpers(
    compiled_session_mock: sessionmaker[Session],
    gmail_smtp_login: str,
    gmail_smtp_password: str,
    email_from_addr: str,
    email_to_addr: str,
) -> Helpers:
    return Helpers(
        gmail_smtp_login,
        gmail_smtp_password,
        email_from_addr,
        email_to_addr,
        compiled_session_mock,
    )


@pytest.fixture
def chat_mock(mocker: MockerFixture) -> Generator[Chat]:
    chat_class_mock = cast(
        type[Chat],
        mocker.patch(
            "telegram.Chat",
            autospec=True,
        ),
    )
    chat_id = 194657302
    chat_mock = chat_class_mock(chat_id, ChatType.PRIVATE)
    yield chat_mock
    del chat_mock


@pytest.fixture
def message_text() -> str:
    return "Hello, World!"


@pytest.fixture
def user_id() -> int:
    return 6573920184


@pytest.fixture
def db_user_mock(
    mocker: MockerFixture,
    user_id: int,
) -> Generator[User]:
    db_user_class_mock = cast(
        type[User],
        mocker.patch(
            "message_sender_telegram_bot.libs.User",
            autospec=True,
        ),
    )
    id_ = UUID("2050c8a2-2dd3-4801-a56f-bc6cf7d5e59e")
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
    # Patched `__init__` can't assign objects to variables by default,
    # so, the fixture assigns `last_send_date` by attribute
    db_user_mock.last_send_date = datetime(2026, 3, 3, 15, 41, 25)
    yield db_user_mock
    del db_user_mock


@pytest.fixture
def db_user_manipulator_mock(
    mocker: MockerFixture,
    db_user_mock: User,
) -> Generator[DBUserManipulator]:
    db_user_manipulator_class_mock = cast(
        type[DBUserManipulator],
        mocker.patch(
            "message_sender_telegram_bot.libs.helpers.DBUserManipulator",
            autospec=True,
            return_value=MagicMock(
                get_owner_status=MagicMock(return_value=False),
            ),
        ),
    )
    db_user_manipulator_mock = db_user_manipulator_class_mock.return_value  # type: ignore[unresolved-attribute]
    yield db_user_manipulator_mock
    del db_user_manipulator_mock


class TestAuthorize:
    @pytest.mark.asyncio
    async def test_detect_of_invalid_token(
        self: Self,
        mocker: MockerFixture,
        helpers: Helpers,
        chat_mock: Chat,
        message_text: str,
        db_user_mock: User,
    ) -> None:
        mocker.patch(
            "message_sender_telegram_bot.libs.helpers.DBValidTokenManipulator",
            autospec=True,
            return_value=MagicMock(
                get=MagicMock(return_value=None),
            ),
        )

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
    async def test_send_of_email(
        self: Self,
        mocker: MockerFixture,
        helpers: Helpers,
        email_from_addr: str,
        email_to_addr: str,
    ) -> None:
        mocker.patch(
            "message_sender_telegram_bot.libs.helpers.GmailSMTPCreator",
            autospec=True,
        )
        email_sender_class_mock = cast(
            type[EmailSender],
            mocker.patch(
                "message_sender_telegram_bot.libs.helpers.EmailSender",
                autospec=True,
            ),
        )
        email_sender_mock = email_sender_class_mock(
            MagicMock(spec=SMTP),
            email_from_addr,
            email_to_addr,
        )
        name = "NAME"
        text = "TEXT"

        await helpers.send_email(name, text)

        email_sender_mock.send.assert_called_once_with(text)  # type: ignore[unresolved-attribute]


class TestShowMessageConfirmationPanel:
    @pytest.mark.asyncio
    async def test_send_of_confirmation_panel_with_message(
        self: Self,
        chat_mock: Chat,
        helpers: Helpers,
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
        reply_markup = InlineKeyboardMarkup(((yes_button, no_button),))

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
    async def test_reject_of_pass_when_cooldown_is_not_passed(
        self: Self,
        mocker: MockerFixture,
        helpers: Helpers,
        db_user_mock: User,
    ) -> None:
        mocker.patch(
            "message_sender_telegram_bot.libs.helpers.datetime",
            autospec=True,
            now=MagicMock(return_value=datetime(2026, 3, 3, 15, 41, 30)),
        )
        mocker.patch(
            (
                "message_sender_telegram_bot.libs.cooldown_checkers."
                "message_send_cooldown_checker.datetime"
            ),
            autospec=True,
            now=MagicMock(return_value=datetime(2026, 3, 3, 15, 41, 30)),
        )
        is_cooldown_passed, remained_time = await helpers.check_cooldown(
            db_user_mock,
        )

        assert isinstance(is_cooldown_passed, bool)
        assert not is_cooldown_passed

        assert isinstance(remained_time, timedelta)
        assert remained_time == timedelta(seconds=25)

    @pytest.mark.asyncio
    async def test_pass_when_cooldown_is_passed(
        self: Self,
        mocker: MockerFixture,
        helpers: Helpers,
        db_user_mock: User,
    ) -> None:
        mocker.patch(
            "message_sender_telegram_bot.libs.helpers.datetime",
            autospec=True,
            now=MagicMock(return_value=datetime(2026, 3, 3, 15, 41, 56)),
        )
        mocker.patch(
            (
                "message_sender_telegram_bot.libs.cooldown_checkers."
                "message_send_cooldown_checker.datetime"
            ),
            autospec=True,
            now=MagicMock(return_value=datetime(2026, 3, 3, 15, 41, 56)),
        )
        is_cooldown_passed, remained_time = await helpers.check_cooldown(
            db_user_mock,
        )

        assert isinstance(is_cooldown_passed, bool)
        assert is_cooldown_passed

        assert isinstance(remained_time, timedelta)
        assert remained_time == timedelta()


class TestIsUserOwner:
    @pytest.mark.asyncio
    async def test_success_output_of_check(
        self: Self,
        helpers: Helpers,
        user_id: int,
        db_user_manipulator_mock: DBUserManipulator,
    ) -> None:
        is_user_owner: bool = await helpers.is_user_owner(user_id)

        assert not is_user_owner
