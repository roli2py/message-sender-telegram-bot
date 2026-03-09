from collections.abc import Generator
from unittest.mock import MagicMock

import pytest
from pytest_mock import MockerFixture
from sqlalchemy import Result, Select
from sqlalchemy.orm import Session, sessionmaker

from message_sender_telegram_bot.libs import (
    DBValidTokenManipulator,
    ValidToken,
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
                    spec=ValidToken,
                ),
            ),
        ),
    )
    db_session_mock = compiled_session_mock()
    db_session_mock.execute = db_session_execute_function_mock  # type: ignore[invalid-assignment]
    yield db_session_mock
    del db_session_mock


@pytest.fixture
def db_valid_token_manipulator(
    db_session_mock: Session,
) -> DBValidTokenManipulator:
    token = "0123456789abcdef"
    return DBValidTokenManipulator(db_session_mock, token)


def test_get_method_of_db_valid_token_manipulator(
    mocker: MockerFixture,
    db_valid_token_manipulator: DBValidTokenManipulator,
) -> None:
    mocker.patch(
        (
            "message_sender_telegram_bot.libs.rdb.manipulators."
            "db_valid_token_manipulator.ValidToken"
        ),
        autospec=True,
    )
    mocker.patch(
        (
            "message_sender_telegram_bot.libs.rdb.manipulators."
            "db_valid_token_manipulator.select"
        ),
        autospec=True,
        return_value=select_instance_mock,
    )
    db_valid_token: ValidToken | None = db_valid_token_manipulator.get()

    assert isinstance(db_valid_token, ValidToken)


def test_create_method_of_db_valid_token_manipulator(
    db_valid_token_manipulator: DBValidTokenManipulator,
) -> None:
    db_valid_token: ValidToken = db_valid_token_manipulator.create()

    assert isinstance(db_valid_token, ValidToken)
