from collections.abc import Generator
from datetime import datetime
from typing import cast
from unittest.mock import MagicMock
from uuid import UUID

import pytest
from pytest_mock import MockerFixture
from sqlalchemy import Result, Select
from sqlalchemy.orm import Session, sessionmaker

from message_sender_telegram_bot.libs import (
    DBMessageManipulator,
    Message,
    User,
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


@pytest.fixture
def db_session_mock(
    compiled_session_mock: sessionmaker[Session],
) -> Generator[Session]:
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
    db_session_mock = compiled_session_mock()
    db_session_mock.execute = db_session_execute_function_mock  # type: ignore[invalid-assignment]
    yield db_session_mock
    del db_session_mock


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
        token=None,
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
def db_message_manipulator_with_req_params(
    db_session_mock: Session,
) -> Generator[DBMessageManipulator]:
    message_id = 1074323464

    db_message_manipulator = DBMessageManipulator(db_session_mock, message_id)
    yield db_message_manipulator
    del db_message_manipulator


@pytest.fixture
def db_message_manipulator_with_req_params_and_sender(
    db_session_mock: Session,
    db_user_mock: User,
) -> Generator[DBMessageManipulator]:
    message_id = 1074323464

    db_message_manipulator = DBMessageManipulator(
        db_session_mock,
        message_id,
        sender=db_user_mock,
    )
    yield db_message_manipulator
    del db_message_manipulator


@pytest.fixture
def db_message_manipulator_with_all_params(
    db_session_mock: Session,
    db_user_mock: User,
) -> Generator[DBMessageManipulator]:
    message_id = 1074323464
    text = "Hello, World!"

    db_message_manipulator = DBMessageManipulator(
        db_session_mock,
        message_id,
        sender=db_user_mock,
        text=text,
    )
    yield db_message_manipulator
    del db_message_manipulator


def test_get_method_db_message_manipulator_with_req_params(
    mocker: MockerFixture,
    db_session_mock: Session,
    db_message_manipulator_with_req_params: DBMessageManipulator,
) -> None:
    mocker.patch(
        (
            "message_sender_telegram_bot.libs.rdb.manipulators."
            "db_message_manipulator.Message"
        ),
        autospec=True,
    )
    mocker.patch(
        (
            "message_sender_telegram_bot.libs.rdb.manipulators."
            "db_message_manipulator.select"
        ),
        autospec=True,
        return_value=select_instance_mock,
    )
    db_message: Message | None = db_message_manipulator_with_req_params.get()

    assert isinstance(db_message, Message)


def test_create_method_db_message_manipulator_with_req_params(
    db_message_manipulator_with_req_params: DBMessageManipulator,
) -> None:
    with pytest.raises(ValueError, match="A sender is absent"):
        db_message_manipulator_with_req_params.create()


def test_create_method_db_message_manipulator_with_req_params_and_sender(
    db_message_manipulator_with_req_params_and_sender: DBMessageManipulator,
) -> None:
    with pytest.raises(ValueError, match="A message text is absent"):
        db_message_manipulator_with_req_params_and_sender.create()


def test_create_method_db_message_manipulator_with_all_params(
    mocker: MockerFixture,
    db_message_manipulator_with_all_params: DBMessageManipulator,
) -> None:
    mocker.patch(
        (
            "message_sender_telegram_bot.libs.rdb.manipulators."
            "db_message_manipulator.Message"
        ),
        autospec=True,
    )
    db_message: Message = db_message_manipulator_with_all_params.create()

    assert isinstance(db_message, Message)
