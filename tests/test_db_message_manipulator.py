from collections.abc import Callable
from typing import Any
from unittest.mock import MagicMock, patch

from pytest import fixture, raises
from sqlalchemy import Result, Select
from sqlalchemy.orm import Session

from message_sender_telegram_bot.libs import (
    DBMessageManipulator,
    Message,
    User,
)

# Session().execute
db_session_execute_function_mock: MagicMock = MagicMock(
    # Session().execute()
    return_value=MagicMock(
        spec=Result,
        # Session().execute().scalar_one_or_none
        scalar_one_or_none=MagicMock(
            # Session().execute().scalar_one_or_none()
            return_value=MagicMock(
                spec=Message,
            ),
        ),
    ),
)

# select()
select_instance_mock: MagicMock = MagicMock(
    spec=Select,
    # select().where
    where=MagicMock(
        # select().where()
        return_value=MagicMock(
            spec=Select,
        )
    ),
)


@fixture
@patch(
    "sqlalchemy.orm.Session",
    spec=Session,
    execute=db_session_execute_function_mock,
)
def db_message_manipulator_with_req_params(
    db_session_mock: Session,
) -> DBMessageManipulator:
    message_id = 1074323464

    return DBMessageManipulator(db_session_mock, message_id)


@fixture
@patch("message_sender_telegram_bot.libs.database_tables.User", spec=User)
@patch(
    "sqlalchemy.orm.Session",
    spec=Session,
    execute=db_session_execute_function_mock,
)
def db_message_manipulator_with_req_params_and_sender(
    db_session_mock: Session,
    db_user_mock: User,
) -> DBMessageManipulator:
    message_id = 1074323464

    return DBMessageManipulator(
        db_session_mock,
        message_id,
        sender=db_user_mock,
    )


@fixture
@patch("message_sender_telegram_bot.libs.database_tables.User", spec=User)
@patch(
    "sqlalchemy.orm.Session",
    spec=Session,
    execute=db_session_execute_function_mock,
)
def db_message_manipulator_with_all_params(
    db_session_mock: Session,
    db_user_mock: User,
) -> DBMessageManipulator:
    message_id = 1074323464
    text = "Hello, World!"

    return DBMessageManipulator(
        db_session_mock,
        message_id,
        sender=db_user_mock,
        text=text,
    )


@patch(
    "message_sender_telegram_bot.libs.db_message_manipulator.select",
    return_value=select_instance_mock,
)
@patch(
    "message_sender_telegram_bot.libs.db_message_manipulator.Message",
    spec=Message,
)
def test_get_method_db_message_manipulator_with_req_params(
    db_message_mock: Message,
    select_function_mock: Callable[
        ...,
        Select[tuple[Any, ...]],
    ],
    db_message_manipulator_with_req_params: DBMessageManipulator,
) -> None:
    db_message: Message | None = db_message_manipulator_with_req_params.get()

    assert isinstance(db_message, Message)


def test_create_method_db_message_manipulator_with_req_params(
    db_message_manipulator_with_req_params: DBMessageManipulator,
) -> None:
    with raises(ValueError, match="A sender is absent"):
        db_message_manipulator_with_req_params.create()


def test_create_method_db_message_manipulator_with_req_params_and_sender(
    db_message_manipulator_with_req_params_and_sender: DBMessageManipulator,
) -> None:
    with raises(ValueError, match="A message text is absent"):
        db_message_manipulator_with_req_params_and_sender.create()


@patch(
    "message_sender_telegram_bot.libs.db_message_manipulator.Message",
    spec=Message,
)
def test_create_method_db_message_manipulator_with_all_params(
    db_message_mock: Message,
    db_message_manipulator_with_all_params: DBMessageManipulator,
) -> None:
    db_message: Message = db_message_manipulator_with_all_params.create()

    assert isinstance(db_message, Message)
