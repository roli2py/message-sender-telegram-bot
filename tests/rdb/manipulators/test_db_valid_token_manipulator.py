from collections.abc import Generator
from unittest.mock import MagicMock

import pytest
from pytest_mock import MockerFixture
from sqlalchemy import Result, Select
from sqlalchemy.orm import Session, sessionmaker

from message_sender_telegram_bot.libs import DBTokenManipulator, Token

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
                    spec=Token,
                ),
            ),
        ),
    )
    db_session_mock = compiled_session_mock()
    db_session_mock.execute = db_session_execute_function_mock  # type: ignore[invalid-assignment]
    yield db_session_mock
    del db_session_mock


@pytest.fixture
def db_token_manipulator(
    db_session_mock: Session,
) -> DBTokenManipulator:
    token = "0123456789abcdef"
    return DBTokenManipulator(db_session_mock, token)


def test_get_method_of_db_token_manipulator(
    mocker: MockerFixture,
    db_token_manipulator: DBTokenManipulator,
) -> None:
    mocker.patch(
        (
            "message_sender_telegram_bot.libs.rdb.manipulators."
            "db_token_manipulator.Token"
        ),
        autospec=True,
    )
    mocker.patch(
        (
            "message_sender_telegram_bot.libs.rdb.manipulators."
            "db_token_manipulator.select"
        ),
        autospec=True,
        return_value=select_instance_mock,
    )
    db_token: Token | None = db_token_manipulator.get()

    assert isinstance(db_token, Token)


def test_create_method_of_db_token_manipulator(
    db_token_manipulator: DBTokenManipulator,
) -> None:
    db_token: Token = db_token_manipulator.create()

    assert isinstance(db_token, Token)
