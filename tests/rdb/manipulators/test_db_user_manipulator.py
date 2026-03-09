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
    DBUserManipulator,
    User,
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
def user_id() -> int:
    return 6573920184


@pytest.fixture
def valid_token_mock(mocker: MockerFixture) -> Generator[ValidToken]:
    valid_token_class_mock = cast(
        type[ValidToken],
        mocker.patch(
            "message_sender_telegram_bot.libs.ValidToken", autospec=True
        ),
    )
    valid_token_mock = valid_token_class_mock(
        id_=UUID("011675fa-cea4-477c-a287-c2367bd8e0b6"),
        token="TOKEN",
        user=None,
    )
    yield valid_token_mock
    del valid_token_mock


@pytest.fixture
def db_user_mock(
    mocker: MockerFixture,
    user_id: int,
    valid_token_mock: ValidToken,
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
        # The fixture will assign `valid_token`, `is_owner` and
        # `last_send_date` later for a reason, described below
        valid_token=None,
        is_owner=False,
        last_send_date=None,
        messages=[],
    )
    # Patched `__init__` can't assign objects to variables by default,
    # so, the fixture assigns `is_owner` and `last_send_date` by
    # attributes
    db_user_mock.valid_token = valid_token_mock
    db_user_mock.is_owner = False
    db_user_mock.last_send_date = datetime(2026, 3, 3, 15, 41, 25)
    yield db_user_mock
    del db_user_mock


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
                    spec=User,
                ),
            ),
        ),
    )
    db_session_mock = compiled_session_mock()
    db_session_mock.execute = db_session_execute_function_mock  # type: ignore[invalid-assignment]
    yield db_session_mock
    del db_session_mock


def test_reject_of_db_user_manipulator_init_without_user_id_and_db_user(
    db_session_mock: Session,
) -> None:
    with pytest.raises(
        ValueError,
        match="A user ID or a DB user must be provided",
    ):
        _ = DBUserManipulator(db_session_mock)  # type: ignore


def test_reject_of_db_user_manipulator_init_with_user_id_and_db_user(
    db_session_mock: Session,
    db_user_mock: User,
) -> None:
    with pytest.raises(
        ValueError, match="Only a user ID or a DB user must be provided"
    ):
        _ = DBUserManipulator(  # type: ignore
            db_session_mock,
            user_id=user_id,
            db_user=db_user_mock,
        )


@pytest.fixture
def db_user_manipulator_with_user_id(
    db_session_mock: Session,
    user_id: int,
) -> Generator[DBUserManipulator]:
    db_user_manipulator = DBUserManipulator(db_session_mock, user_id=user_id)
    yield db_user_manipulator
    del db_user_manipulator


@pytest.fixture
def db_user_manipulator_with_db_user(
    mocker: MockerFixture,
    db_session_mock: Session,
    db_user_mock: User,
) -> Generator[DBUserManipulator]:
    db_user_manipulator = DBUserManipulator(
        db_session_mock,
        db_user=db_user_mock,
    )
    yield db_user_manipulator
    del db_user_manipulator


def test_get_method_of_db_user_manipulator_with_user_id(
    mocker: MockerFixture,
    db_user_mock: User,
    db_user_manipulator_with_user_id: DBUserManipulator,
) -> None:
    mocker.patch(
        (
            "message_sender_telegram_bot.libs.rdb.manipulators."
            "db_user_manipulator.select"
        ),
        autospec=True,
        return_value=select_instance_mock,
    )
    db_user: User | None = db_user_manipulator_with_user_id.get()

    assert isinstance(db_user, User)


def test_get_method_of_db_user_manipulator_with_db_user(
    db_user_manipulator_with_db_user: DBUserManipulator,
    db_user_mock: User,
) -> None:
    with pytest.raises(
        ValueError,
        match="A user ID is absent",
    ):
        db_user_manipulator_with_db_user.get()


def test_create_method_of_db_user_manipulator_with_user_id(
    db_user_manipulator_with_user_id: DBUserManipulator,
    db_user_mock: User,
) -> None:
    db_user: User = db_user_manipulator_with_user_id.create()

    assert isinstance(db_user, User)


def test_create_method_of_db_user_manipulator_with_db_user(
    db_user_manipulator_with_db_user: DBUserManipulator,
    db_user_mock: User,
) -> None:
    with pytest.raises(
        ValueError,
        match="A user ID is absent",
    ):
        db_user_manipulator_with_db_user.create()


def test_get_authorizing_status_method_of_db_user_manipulator_with_user_id(
    db_user_manipulator_with_user_id: DBUserManipulator,
) -> None:
    with pytest.raises(
        ValueError,
        match="A DB user is absent",
    ):
        db_user_manipulator_with_user_id.get_authorizing_status()


def test_get_authorizing_status_method_of_db_user_manipulator_with_db_user(
    db_user_manipulator_with_db_user: DBUserManipulator,
) -> None:
    is_user_authorizing: bool = (
        db_user_manipulator_with_db_user.get_authorizing_status()
    )

    assert isinstance(is_user_authorizing, bool)


def test_get_valid_token_method_of_db_user_manipulator_with_user_id(
    db_user_manipulator_with_user_id: DBUserManipulator,
) -> None:
    with pytest.raises(
        ValueError,
        match="A DB user is absent",
    ):
        db_user_manipulator_with_user_id.get_valid_token()


def test_get_valid_token_method_of_db_user_manipulator_with_db_user(
    db_user_manipulator_with_db_user: DBUserManipulator,
) -> None:
    valid_token: ValidToken | None = (
        db_user_manipulator_with_db_user.get_valid_token()
    )

    assert isinstance(valid_token, ValidToken)


def test_set_authorizing_status_method_of_db_user_manipulator_with_user_id(
    db_user_manipulator_with_user_id: DBUserManipulator,
) -> None:
    with pytest.raises(
        ValueError,
        match="A DB user is absent",
    ):
        db_user_manipulator_with_user_id.set_authorizing_status(True)


def test_set_authorizing_status_method_of_db_user_manipulator_with_db_user(
    db_user_manipulator_with_db_user: DBUserManipulator,
) -> None:
    db_user_manipulator_with_db_user.set_authorizing_status(True)


def test_set_valid_token_method_of_db_user_manipulator_with_user_id(
    db_user_manipulator_with_user_id: DBUserManipulator,
    valid_token_mock: ValidToken,
) -> None:
    with pytest.raises(
        ValueError,
        match="A DB user is absent",
    ):
        db_user_manipulator_with_user_id.set_valid_token(valid_token_mock)


def test_set_valid_token_method_of_db_user_manipulator_with_db_user(
    db_user_manipulator_with_db_user: DBUserManipulator,
    valid_token_mock: ValidToken,
) -> None:
    db_user_manipulator_with_db_user.set_valid_token(valid_token_mock)


def test_clear_valid_token_method_of_db_user_manipulator_with_user_id(
    db_user_manipulator_with_user_id: DBUserManipulator,
) -> None:
    with pytest.raises(
        ValueError,
        match="A DB user is absent",
    ):
        db_user_manipulator_with_user_id.clear_valid_token()


def test_clear_valid_token_method_of_db_user_manipulator_with_db_user(
    db_user_manipulator_with_db_user: DBUserManipulator,
) -> None:
    db_user_manipulator_with_db_user.clear_valid_token()


def test_get_owner_status_method_of_db_user_manipulator_with_user_id(
    db_user_manipulator_with_user_id: DBUserManipulator,
) -> None:
    with pytest.raises(
        ValueError,
        match="A DB user is absent",
    ):
        _ = db_user_manipulator_with_user_id.get_owner_status()


def test_get_owner_status_method_of_db_user_manipulator_with_db_user(
    db_user_manipulator_with_db_user: DBUserManipulator,
) -> None:
    is_user_owner: bool = db_user_manipulator_with_db_user.get_owner_status()

    assert isinstance(is_user_owner, bool)
    assert not is_user_owner
