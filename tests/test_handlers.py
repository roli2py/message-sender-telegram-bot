from typing import Self
from unittest.mock import AsyncMock, MagicMock, patch

import pytest
from sqlalchemy.orm import Session, sessionmaker
from telegram import Chat, Update, User
from telegram.ext import ContextTypes

from message_sender_telegram_bot.libs import Handlers, Helpers
from message_sender_telegram_bot.libs.consts import Answers


@pytest.fixture
@patch("message_sender_telegram_bot.libs.Helpers", autospec=True)
def handlers(
    helpers_mock: Helpers,
    compiled_session_mock: sessionmaker[Session],
) -> Handlers:
    return Handlers(compiled_session_mock, helpers_mock)


# TODO fix a sharing of the object between tests
@pytest.fixture
@patch(
    "telegram.Update",
    autospec=True,
    return_value=MagicMock(
        effective_chat=MagicMock(
            spec=Chat,
            send_message=AsyncMock(),
        ),
        effective_user=MagicMock(spec=User),
    ),
)
def update_obj_mock(update_obj_class_mock: type[Update]) -> Update:
    update_id = 5192443746
    return update_obj_class_mock(update_id)


@pytest.fixture
@patch("telegram.ext.ContextTypes", autospec=True)
def ctx_mock(ctx_class_mock: type[ContextTypes]) -> ContextTypes:
    return ctx_class_mock()


class TestStart:
    # What is need to test:
    # - [x] chat is None
    # - [x] user is None
    # - [ ] db_user is None
    # - [ ] is_user_authorizing
    # - [ ] valid_token is None
    # - [ ] without conditions above eg. user have been passed all challenges
    #       and no bugs have been invoked
    @pytest.mark.xfail(reason="Mock objects shares their states")
    @pytest.mark.asyncio
    async def test_stop_of_handle_when_chat_is_absent(
        self: Self,
        handlers: Handlers,
        update_obj_mock: Update,
        ctx_mock: ContextTypes,
    ) -> None:
        update_obj_mock.effective_chat = None  # type: ignore[invalid-assignment]

        await handlers.start(update_obj_mock, ctx_mock)

        update_obj_mock.effective_user.assert_not_called()  # type: ignore[unresolved-attribute]

    @pytest.mark.xfail(reason="Mock objects shares their states")
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
            Answers.UNKNOWN_ERROR_OCCURS,
        )


class TestHandleMessage:
    pass


class TestSend:
    pass


class TestCancel:
    pass


class TestNotifyAboutUnknownCommand:
    pass


class TestShowAdminPanel:
    pass


class TestGenerateToken:
    pass
