from collections.abc import Generator
from datetime import timedelta
from typing import Self, cast
from unittest.mock import AsyncMock, MagicMock

import pytest
import telegram
from pytest_mock import MockerFixture
from sqlalchemy.orm import Session, sessionmaker
from telegram import (
    CallbackQuery,
    Chat,
    InlineKeyboardButton,
    InlineKeyboardMarkup,
    Update,
)
from telegram.constants import ChatType, ParseMode
from telegram.ext import ContextTypes

from message_sender_telegram_bot.libs import (
    DBMessageManipulator,
    DBUserManipulator,
    DBValidTokenManipulator,
    Handlers,
    Helpers,
    ValidToken,
    consts,
    fstrings,
)
from message_sender_telegram_bot.libs.consts import ButtonTexts
from message_sender_telegram_bot.libs.rdb import database_tables
from message_sender_telegram_bot.libs.types import CooldownCheckResult, Token


@pytest.fixture
def helpers_mock(
    mocker: MockerFixture,
    compiled_session_mock: sessionmaker[Session],
) -> Generator[Helpers]:
    gmail_smtp_login = "GMAIL_SMTP_LOGIN"
    gmail_smtp_password = "GMAIL_SMTP_PASSWORD"
    email_from_addr = "EMAIL_FROM_ADDR"
    email_to_addr = "EMAIL_TO_ADDR"

    helpers_class_mock = cast(
        type[Helpers],
        mocker.patch(
            "message_sender_telegram_bot.libs.Helpers",
            autospec=True,
            return_value=MagicMock(
                authorize=AsyncMock(),
                check_cooldown=AsyncMock(
                    return_value=CooldownCheckResult(
                        True,
                        timedelta(),
                    ),
                ),
                show_message_confirmation_panel=AsyncMock(),
                is_user_owner=AsyncMock(return_value=True),
            ),
        ),
    )
    helpers_mock: Helpers = helpers_class_mock(
        gmail_smtp_login,
        gmail_smtp_password,
        email_from_addr,
        email_to_addr,
        compiled_session_mock,
    )
    yield helpers_mock
    del helpers_mock


@pytest.fixture
def handlers(
    helpers_mock: Helpers,
    compiled_session_mock: sessionmaker[Session],
) -> Handlers:
    return Handlers(compiled_session_mock, helpers_mock)


@pytest.fixture
def update_obj_mock(mocker: MockerFixture) -> Generator[Update]:
    update_obj_class_mock = mocker.patch(
        "telegram.Update",
        autospec=True,
        return_value=MagicMock(
            callback_query=MagicMock(
                spec=CallbackQuery,
                answer=AsyncMock(),
            ),
            effective_chat=MagicMock(
                spec=Chat,
                type=ChatType.PRIVATE,
                send_message=AsyncMock(),
            ),
            effective_user=MagicMock(
                spec=telegram.User,
                send_message=AsyncMock(),
            ),
            effective_message=MagicMock(spec=telegram.Message),
        ),
    )
    update_id = 5192443746
    update_obj_mock: Update = update_obj_class_mock(update_id)
    yield update_obj_mock
    del update_obj_mock


@pytest.fixture
def ctx_mock(mocker: MockerFixture) -> Generator[ContextTypes]:
    ctx_class_mock = mocker.patch("telegram.ext.ContextTypes", autospec=True)
    ctx_mock: ContextTypes = ctx_class_mock()
    yield ctx_mock
    del ctx_mock


@pytest.fixture
def message_text() -> str:
    return "Text"


@pytest.fixture
def message_mock(
    mocker: MockerFixture,
    message_text: str,
) -> Generator[telegram.Message]:
    message_class_mock = mocker.patch(
        "telegram.Message",
        autospec=True,
        text=message_text,
    )
    yield message_class_mock
    del message_class_mock


@pytest.fixture
def db_user_manipulator_mock(
    mocker: MockerFixture,
) -> Generator[DBUserManipulator]:
    db_user_manipulator_class_mock = cast(
        type[DBUserManipulator],
        mocker.patch(
            "message_sender_telegram_bot.libs.handlers.DBUserManipulator",
            autospec=True,
            return_value=MagicMock(
                get=MagicMock(
                    return_value=MagicMock(spec=database_tables.User),
                ),
                get_authorizing_status=MagicMock(return_value=False),
                get_valid_token=MagicMock(
                    return_value=MagicMock(spec=ValidToken),
                ),
            ),
        ),
    )
    db_user_manipulator_mock = db_user_manipulator_class_mock.return_value  # type: ignore[unresolved-attribute]
    yield db_user_manipulator_mock
    del db_user_manipulator_mock


@pytest.fixture
def db_message_manipulator_mock(
    mocker: MockerFixture,
) -> Generator[DBMessageManipulator]:
    db_session_mock = MagicMock(spec=Session)
    message_id = 436583812
    db_user_mock = MagicMock(spec=database_tables.User)
    text = "Text"

    db_message_manipulator_class_mock = cast(
        type[DBMessageManipulator],
        mocker.patch(
            "message_sender_telegram_bot.libs.handlers.DBMessageManipulator",
            autospec=True,
        ),
    )
    db_message_manipulator_mock = db_message_manipulator_class_mock(
        db_session_mock,
        message_id,
        sender=db_user_mock,  # type: ignore[invalid-argument-type]
        text=text,
    )
    yield db_message_manipulator_mock
    del db_message_manipulator_mock


@pytest.fixture
def db_valid_token_manipulator_mock(
    mocker: MockerFixture,
) -> Generator[DBValidTokenManipulator]:
    db_session_mock = MagicMock(spec=Session)
    token = Token("TOKEN")

    db_valid_token_manipulator_class_mock = cast(
        type[DBValidTokenManipulator],
        mocker.patch(
            "message_sender_telegram_bot.libs.handlers.DBValidTokenManipulator",
            autospec=True,
        ),
    )
    db_valid_token_manipulator_mock = db_valid_token_manipulator_class_mock(
        db_session_mock,
        token,
    )
    yield db_valid_token_manipulator_mock
    del db_valid_token_manipulator_mock


class TestStart:
    @pytest.mark.asyncio
    async def test_stop_of_handle_when_chat_is_absent(
        self: Self,
        handlers: Handlers,
        update_obj_mock: Update,
        ctx_mock: ContextTypes,
    ) -> None:
        update_obj_mock.effective_chat = None  # type: ignore[invalid-assignment]

        await handlers.start(update_obj_mock, ctx_mock)

        # TODO find a way to test that a `chat is None` construction was
        # invoked

    @pytest.mark.asyncio
    async def test_stop_of_handle_when_user_is_absent(
        self: Self,
        handlers: Handlers,
        update_obj_mock: Update,
        ctx_mock: ContextTypes,
    ) -> None:
        update_obj_mock.effective_user = None  # type: ignore[invalid-assignment]

        await handlers.start(update_obj_mock, ctx_mock)

        update_obj_mock.effective_chat.send_message.assert_called_once_with(  # type: ignore[unresolved-attribute]
            consts.Answers.UNKNOWN_ERROR_OCCURS,
        )

    @pytest.mark.asyncio
    async def test_creation_db_user_and_stop_of_handle_when_db_user_is_absent(
        self: Self,
        handlers: Handlers,
        update_obj_mock: Update,
        ctx_mock: ContextTypes,
        db_user_manipulator_mock: DBUserManipulator,
    ) -> None:
        db_user_manipulator_mock.get.return_value = None  # type: ignore[unresolved-attribute]

        await handlers.start(update_obj_mock, ctx_mock)

        db_user_manipulator_mock.create.assert_called_once()  # type: ignore[unresolved-attribute]

        update_obj_mock.effective_chat.send_message.assert_called_once_with(  # type: ignore[unresolved-attribute]
            consts.Answers.ENTER_TOKEN,
        )

    @pytest.mark.asyncio
    async def test_stop_of_handle_when_user_is_authorizing(
        self: Self,
        handlers: Handlers,
        update_obj_mock: Update,
        ctx_mock: ContextTypes,
        db_user_manipulator_mock: DBUserManipulator,
    ) -> None:
        db_user_manipulator_mock.get_authorizing_status.return_value = True  # type: ignore[unresolved-attribute]

        await handlers.start(update_obj_mock, ctx_mock)

        db_user_manipulator_mock.get_authorizing_status.assert_called_once()  # type: ignore[unresolved-attribute]

        update_obj_mock.effective_chat.send_message.assert_called_once_with(  # type: ignore[unresolved-attribute]
            consts.Answers.ENTER_TOKEN,
        )

    @pytest.mark.asyncio
    async def test_stop_of_handle_when_valid_token_is_absent(
        self: Self,
        handlers: Handlers,
        update_obj_mock: Update,
        ctx_mock: ContextTypes,
        db_user_manipulator_mock: DBUserManipulator,
    ) -> None:
        db_user_manipulator_mock.get_valid_token.return_value = None  # type: ignore[unresolved-attribute]

        await handlers.start(update_obj_mock, ctx_mock)

        # Assigning a function to a variable to make a line smaller than
        # 79 symbols
        set_authorizing_status_func = (
            db_user_manipulator_mock.set_authorizing_status
        )
        set_authorizing_status_func.assert_called_once_with(True)  # type: ignore[unresolved-attribute]

        update_obj_mock.effective_chat.send_message.assert_called_once_with(  # type: ignore[unresolved-attribute]
            consts.Answers.TOKEN_IS_EXPIRED,
        )

    @pytest.mark.asyncio
    async def test_success_authorization(
        self: Self,
        handlers: Handlers,
        update_obj_mock: Update,
        ctx_mock: ContextTypes,
        db_user_manipulator_mock: DBUserManipulator,
    ) -> None:
        await handlers.start(update_obj_mock, ctx_mock)

        update_obj_mock.effective_chat.send_message.assert_called_once_with(  # type: ignore[unresolved-attribute]
            consts.Answers.AUTHORIZED,
        )


class TestHandleMessage:
    @pytest.mark.asyncio
    async def test_stop_of_handle_when_chat_is_absent(
        self: Self,
        handlers: Handlers,
        update_obj_mock: Update,
        ctx_mock: ContextTypes,
    ) -> None:
        update_obj_mock.effective_chat = None  # type: ignore[invalid-assignment]

        await handlers.handle_message(update_obj_mock, ctx_mock)

        # TODO find a way to test that a `chat is None` construction was
        # invoked

    @pytest.mark.asyncio
    async def test_stop_of_handle_when_user_is_absent(
        self: Self,
        handlers: Handlers,
        update_obj_mock: Update,
        ctx_mock: ContextTypes,
    ) -> None:
        update_obj_mock.effective_message = None  # type: ignore[invalid-assignment]

        await handlers.handle_message(update_obj_mock, ctx_mock)

        update_obj_mock.effective_chat.send_message.assert_called_once_with(  # type: ignore[unresolved-attribute]
            consts.Answers.UNKNOWN_ERROR_OCCURS,
        )

    @pytest.mark.asyncio
    async def test_stop_of_handle_when_message_is_absent(
        self: Self,
        handlers: Handlers,
        update_obj_mock: Update,
        ctx_mock: ContextTypes,
        message_mock: telegram.Message,
    ) -> None:
        update_obj_mock.effective_message = None  # type: ignore[invalid-assignment]

        await handlers.handle_message(update_obj_mock, ctx_mock)

        update_obj_mock.effective_chat.send_message.assert_called_once_with(  # type: ignore[unresolved-attribute]
            consts.Answers.UNKNOWN_ERROR_OCCURS,
        )

    @pytest.mark.asyncio
    async def test_stop_of_handle_when_message_text_is_absent(
        self: Self,
        handlers: Handlers,
        update_obj_mock: Update,
        ctx_mock: ContextTypes,
        message_mock: telegram.Message,
    ) -> None:
        update_obj_mock.effective_message.text = None  # type: ignore[invalid-assignment]

        await handlers.handle_message(update_obj_mock, ctx_mock)

        update_obj_mock.effective_chat.send_message.assert_called_once_with(  # type: ignore[unresolved-attribute]
            consts.Answers.MESSAGE_DOESNT_HAVE_TEXT,
        )

    @pytest.mark.asyncio
    async def test_stop_of_handle_when_db_user_is_absent(
        self: Self,
        handlers: Handlers,
        update_obj_mock: Update,
        ctx_mock: ContextTypes,
        db_user_manipulator_mock: DBUserManipulator,
    ) -> None:
        db_user_manipulator_mock.get.return_value = None  # type: ignore[unresolved-attribute]

        await handlers.handle_message(update_obj_mock, ctx_mock)

        update_obj_mock.effective_chat.send_message.assert_called_once_with(  # type: ignore[unresolved-attribute]
            consts.Answers.NOT_AUTHORIZED,
        )

    @pytest.mark.asyncio
    async def test_stop_of_handle_when_user_is_authorizing(
        self: Self,
        handlers: Handlers,
        update_obj_mock: Update,
        ctx_mock: ContextTypes,
        db_user_manipulator_mock: DBUserManipulator,
        helpers_mock: Helpers,
    ) -> None:
        db_user_manipulator_mock.get_authorizing_status.return_value = True  # type: ignore[unresolved-attribute]

        await handlers.handle_message(update_obj_mock, ctx_mock)

        helpers_mock.authorize.assert_called_once()  # type: ignore[unresolved-attribute]

    @pytest.mark.asyncio
    async def test_stop_of_handle_when_cooldown_is_not_passed(
        self: Self,
        handlers: Handlers,
        update_obj_mock: Update,
        ctx_mock: ContextTypes,
        db_user_manipulator_mock: DBUserManipulator,
        helpers_mock: Helpers,
    ) -> None:
        cooldown_check_result = CooldownCheckResult(
            False,
            timedelta(seconds=15),
        )
        helpers_mock.check_cooldown.return_value = cooldown_check_result  # type: ignore[unresolved-attribute]

        await handlers.handle_message(update_obj_mock, ctx_mock)

        update_obj_mock.effective_chat.send_message.assert_called_once_with(  # type: ignore[unresolved-attribute]
            fstrings.Answers.send_message_after_seconds.format(
                seconds=cooldown_check_result.remained_time.seconds,
            ),
        )

    @pytest.mark.asyncio
    async def test_success_show_of_message_confirmation_panel(
        self: Self,
        handlers: Handlers,
        update_obj_mock: Update,
        ctx_mock: ContextTypes,
        db_user_manipulator_mock: DBUserManipulator,
        helpers_mock: Helpers,
        # The fixture patches a DB message manipulator to successfully
        # finish a handle
        db_message_manipulator_mock: DBMessageManipulator,
    ) -> None:
        await handlers.handle_message(update_obj_mock, ctx_mock)

        chat_mock = update_obj_mock.effective_chat
        message_mock = update_obj_mock.effective_message
        assert message_mock is not None
        helpers_mock.show_message_confirmation_panel.assert_called_once_with(  # type: ignore[unresolved-attribute]
            chat_mock,
            message_mock.id,
        )


class TestSend:
    # What do I need to test?:
    # - [ ] chat is None
    # - [ ] user is None or message is None
    # - [ ] db_user is None
    # - [ ] is_user_authorizing
    # - [ ] not is_cooldown_passed
    # - [ ] callback_query is None
    # - [ ] callback_data is None
    # - [ ] db_message is None
    # - [ ] db_message.sender_id != db_user.id_
    # - [ ] db_message.is_sent
    # - [ ] none of the cases above
    pass


class TestCancel:
    # What do I need to test?:
    # - [ ] chat is None
    # - [ ] user is None
    # - [ ] db_user is not None
    #     - [ ] is_user_authorizing
    # - [ ] callback_query is not None
    #     - [ ] message is None or callback_data is None
    #     - [ ] db_message is None
    #     - [ ] db_user is None or db_message.sender_id != db_user.id_
    #     - [ ] db_message.is_sent
    # - [ ] none of the cases above
    pass


class TestNotifyAboutUnknownCommand:
    @pytest.mark.asyncio
    async def test_stop_of_handle_when_chat_is_absent(
        self: Self,
        handlers: Handlers,
        update_obj_mock: Update,
        ctx_mock: ContextTypes,
    ) -> None:
        update_obj_mock.effective_chat = None  # type: ignore[invalid-assignment]

        await handlers.notify_about_unknown_command(update_obj_mock, ctx_mock)

        # TODO find a way to test that a `chat is None` construction was
        # invoked

    @pytest.mark.asyncio
    async def test_success_message_sending_about_unknown_command(
        self: Self,
        handlers: Handlers,
        update_obj_mock: Update,
        ctx_mock: ContextTypes,
    ) -> None:
        await handlers.notify_about_unknown_command(update_obj_mock, ctx_mock)

        update_obj_mock.effective_chat.send_message.assert_called_once_with(  # type: ignore[unresolved-attribute]
            consts.Answers.UNKNOWN_COMMAND,
        )


class TestShowAdminPanel:
    @pytest.mark.asyncio
    async def test_stop_of_handle_when_chat_is_absent(
        self: Self,
        handlers: Handlers,
        update_obj_mock: Update,
        ctx_mock: ContextTypes,
    ) -> None:
        update_obj_mock.effective_chat = None  # type: ignore[invalid-assignment]

        await handlers.show_admin_panel(update_obj_mock, ctx_mock)

        # TODO find a way to test that a `chat is None` construction was
        # invoked

    @pytest.mark.asyncio
    async def test_stop_of_handle_when_user_is_absent(
        self: Self,
        handlers: Handlers,
        update_obj_mock: Update,
        ctx_mock: ContextTypes,
    ) -> None:
        update_obj_mock.effective_user = None  # type: ignore[invalid-assignment]

        await handlers.show_admin_panel(update_obj_mock, ctx_mock)

        update_obj_mock.effective_chat.send_message.assert_called_once_with(  # type: ignore[unresolved-attribute]
            consts.Answers.UNKNOWN_ERROR_OCCURS,
        )

    @pytest.mark.asyncio
    async def test_stop_of_handle_when_user_is_not_owner(
        self: Self,
        handlers: Handlers,
        update_obj_mock: Update,
        ctx_mock: ContextTypes,
        helpers_mock: Helpers,
    ) -> None:
        helpers_mock.is_user_owner.return_value = False  # type: ignore[unresolved-attribute]

        await handlers.show_admin_panel(update_obj_mock, ctx_mock)

        update_obj_mock.effective_chat.send_message.assert_called_once_with(  # type: ignore[unresolved-attribute]
            consts.Answers.NOT_OWNER_OF_BOT,
        )

    @pytest.mark.asyncio
    async def test_success_show_of_admin_panel(
        self: Self,
        handlers: Handlers,
        update_obj_mock: Update,
        ctx_mock: ContextTypes,
        helpers_mock: Helpers,
    ) -> None:
        reply_markup = InlineKeyboardMarkup(
            (
                (
                    InlineKeyboardButton(
                        ButtonTexts.GENERATE_TOKEN,
                        callback_data="generate_token",
                    ),
                ),
            ),
        )

        await handlers.show_admin_panel(update_obj_mock, ctx_mock)

        update_obj_mock.effective_chat.send_message.assert_called_once_with(  # type: ignore[unresolved-attribute]
            consts.Answers.WHAT_DO_YOU_WANT,
            reply_markup=reply_markup,
        )


class TestGenerateToken:
    @pytest.mark.asyncio
    async def test_stop_of_handle_when_chat_is_absent(
        self: Self,
        handlers: Handlers,
        update_obj_mock: Update,
        ctx_mock: ContextTypes,
    ) -> None:
        update_obj_mock.effective_chat = None  # type: ignore[invalid-assignment]

        await handlers.generate_token(update_obj_mock, ctx_mock)

        # TODO find a way to test that a `chat is None` construction was
        # invoked

    @pytest.mark.asyncio
    async def test_stop_of_handle_when_user_is_absent(
        self: Self,
        handlers: Handlers,
        update_obj_mock: Update,
        ctx_mock: ContextTypes,
    ) -> None:
        update_obj_mock.effective_user = None  # type: ignore[invalid-assignment]

        await handlers.generate_token(update_obj_mock, ctx_mock)

        update_obj_mock.effective_chat.send_message.assert_called_once_with(  # type: ignore[unresolved-attribute]
            consts.Answers.UNKNOWN_ERROR_OCCURS,
        )

    @pytest.mark.asyncio
    async def test_stop_of_handle_when_callback_query_is_absent(
        self: Self,
        handlers: Handlers,
        update_obj_mock: Update,
        ctx_mock: ContextTypes,
    ) -> None:
        update_obj_mock.callback_query = None

        await handlers.generate_token(update_obj_mock, ctx_mock)

        update_obj_mock.effective_chat.send_message.assert_called_once_with(  # type: ignore[unresolved-attribute]
            consts.Answers.UNKNOWN_ERROR_OCCURS,
        )

    @pytest.mark.asyncio
    async def test_stop_of_handle_when_user_is_not_owner(
        self: Self,
        handlers: Handlers,
        update_obj_mock: Update,
        ctx_mock: ContextTypes,
        helpers_mock: Helpers,
    ) -> None:
        helpers_mock.is_user_owner.return_value = False  # type: ignore[unresolved-attribute]

        await handlers.generate_token(update_obj_mock, ctx_mock)

        update_obj_mock.effective_chat.send_message.assert_called_once_with(  # type: ignore[unresolved-attribute]
            consts.Answers.NOT_OWNER_OF_BOT,
        )

    @pytest.mark.asyncio
    async def test_success_token_generation_not_in_dm(
        self: Self,
        handlers: Handlers,
        update_obj_mock: Update,
        ctx_mock: ContextTypes,
        helpers_mock: Helpers,
    ) -> None:
        chat_mock = update_obj_mock.effective_chat
        chat_mock.type = ChatType.GROUP  # type: ignore[invalid-assignment]

        await handlers.generate_token(update_obj_mock, ctx_mock)

        chat_mock.send_message.assert_called_once_with(  # type: ignore[unresolved-attribute]
            consts.Answers.SENT_TOKEN_TO_DM,
        )

    @pytest.mark.asyncio
    async def test_success_token_generation_in_dm(
        self: Self,
        mocker: MockerFixture,
        handlers: Handlers,
        update_obj_mock: Update,
        ctx_mock: ContextTypes,
        helpers_mock: Helpers,
        # The fixture patches a DB valid token manipulator to
        # successfully finish a handle
        db_valid_token_manipulator_mock: DBValidTokenManipulator,
    ) -> None:
        token = "TOKEN"
        mocker.patch(
            "message_sender_telegram_bot.libs.handlers.token_hex",
            return_value=token,
        )

        await handlers.generate_token(update_obj_mock, ctx_mock)

        update_obj_mock.effective_user.send_message.assert_called_once_with(  # type: ignore[unresolved-attribute]
            fstrings.Answers.new_token.format(token=token),
            parse_mode=ParseMode.MARKDOWN_V2,
        )
