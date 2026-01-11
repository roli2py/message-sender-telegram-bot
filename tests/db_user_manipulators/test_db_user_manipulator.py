from collections.abc import Callable
from typing import Any
from unittest.mock import MagicMock, patch

from pytest import fixture, raises
from sqlalchemy import Result, Select
from sqlalchemy.orm import Session

from libs import DBUserManipulator, User

user_id = 1234567
token = "0123456789abcdef"


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


@patch("sqlalchemy.orm.Session", spec=Session)
def test_reject_of_db_user_manipulator_init_without_user_id_and_db_user(
    db_session_mock: Session,
) -> None:
    with raises(ValueError, match="A user ID or a DB user must be provided"):
        _ = DBUserManipulator(
            db_session_mock
        )  # pyright: ignore[reportCallIssue]  # type: ignore


@patch("libs.User", spec=User)
@patch("sqlalchemy.orm.Session", spec=Session)
def test_a_reject_of_a_db_user_manipulator_init_with_a_user_id_and_a_db_user(
    db_session_mock: Session,
    db_user_mock: User,
) -> None:
    with raises(
        ValueError, match="Only a user ID or a DB user must be provided"
    ):
        _ = DBUserManipulator(  # pyright: ignore[reportCallIssue]  # type: ignore
            db_session_mock,
            user_id=user_id,
            db_user=db_user_mock,
        )


@fixture
@patch(
    "sqlalchemy.orm.Session",
    spec=Session,
    execute=db_session_execute_function_mock,
)
def db_user_manipulator_with_a_user_id(
    db_session_mock: Session,
) -> DBUserManipulator:
    return DBUserManipulator(db_session_mock, user_id=user_id)


@fixture
@patch(
    "libs.User", spec=User, user_id=user_id, token=token, is_authorizing=True
)
@patch(
    "sqlalchemy.orm.Session",
    spec=Session,
    execute=db_session_execute_function_mock,
)
def db_user_manipulator_with_a_db_user(
    db_session_mock: Session, db_user_mock: User
) -> DBUserManipulator:
    return DBUserManipulator(db_session_mock, db_user=db_user_mock)


@patch(
    "libs.db_user_manipulators.db_user_manipulator.select",
    return_value=select_instance_mock,
)
@patch(
    "libs.db_user_manipulators.db_user_manipulator.User",
    spec=User,
)
def test_a_get_method_of_db_user_manipulator_with_a_user_id(
    db_user_mock: User,  # pyright: ignore[reportUnusedParameter]  # type: ignore
    select_function_mock: Callable[  # pyright: ignore[reportUnusedParameter]  # type: ignore
        ...,
        Select[
            tuple[
                Any, ...  # pyright: ignore[reportExplicitAny]  # type: ignore
            ]
        ],
    ],
    db_user_manipulator_with_a_user_id: DBUserManipulator,
) -> None:
    db_user: User | None = db_user_manipulator_with_a_user_id.get()

    assert isinstance(db_user, User)


@patch(
    "libs.db_user_manipulators.db_user_manipulator.User",
    spec=User,
)
def test_a_get_method_of_db_user_manipulator_with_a_db_user(
    _,
    db_user_manipulator_with_a_db_user: DBUserManipulator,
) -> None:
    with raises(ValueError, match="A user ID is absent"):
        _ = db_user_manipulator_with_a_db_user.get()


@patch(
    "libs.db_user_manipulators.db_user_manipulator.User",
    spec=User,
)
def test_a_create_method_of_db_user_manipulator_with_a_user_id(
    _,
    db_user_manipulator_with_a_user_id: DBUserManipulator,
) -> None:
    db_user: User = db_user_manipulator_with_a_user_id.create()

    assert isinstance(db_user, User)


@patch(
    "libs.db_user_manipulators.db_user_manipulator.User",
    spec=User,
)
def test_a_create_method_of_db_user_manipulator_with_a_db_user(
    _,
    db_user_manipulator_with_a_db_user: DBUserManipulator,
) -> None:
    with raises(ValueError, match="A user ID is absent"):
        _ = db_user_manipulator_with_a_db_user.create()


def test_a_get_authorizing_status_method_of_db_user_manipulator_with_a_user_id(
    db_user_manipulator_with_a_user_id: DBUserManipulator,
) -> None:
    with raises(ValueError, match="A DB user is absent"):
        _ = db_user_manipulator_with_a_user_id.get_authorizing_status()


def test_a_get_authorizing_status_method_of_db_user_manipulator_with_a_db_user(
    db_user_manipulator_with_a_db_user: DBUserManipulator,
) -> None:
    is_user_authorizing: bool = (
        db_user_manipulator_with_a_db_user.get_authorizing_status()
    )

    assert isinstance(is_user_authorizing, bool)


def test_a_get_token_method_of_db_user_manipulator_with_a_user_id(
    db_user_manipulator_with_a_user_id: DBUserManipulator,
) -> None:
    with raises(ValueError, match="A DB user is absent"):
        _ = db_user_manipulator_with_a_user_id.get_token()


def test_a_get_token_method_of_db_user_manipulator_with_a_db_user(
    db_user_manipulator_with_a_db_user: DBUserManipulator,
) -> None:
    token: str | None = db_user_manipulator_with_a_db_user.get_token()

    assert isinstance(token, str)


def test_a_set_authorizing_status_method_of_db_user_manipulator_with_a_user_id(
    db_user_manipulator_with_a_user_id: DBUserManipulator,
) -> None:
    with raises(ValueError, match="A DB user is absent"):
        db_user_manipulator_with_a_user_id.set_authorizing_status(True)


def test_a_set_authorizing_status_method_of_db_user_manipulator_with_a_db_user(
    db_user_manipulator_with_a_db_user: DBUserManipulator,
) -> None:
    db_user_manipulator_with_a_db_user.set_authorizing_status(True)


def test_a_set_token_method_of_db_user_manipulator_with_a_user_id(
    db_user_manipulator_with_a_user_id: DBUserManipulator,
) -> None:
    with raises(ValueError, match="A DB user is absent"):
        _ = db_user_manipulator_with_a_user_id.set_token(token)


def test_a_set_token_method_of_db_user_manipulator_with_a_db_user(
    db_user_manipulator_with_a_db_user: DBUserManipulator,
) -> None:
    db_user_manipulator_with_a_db_user.set_token(token)


def test_a_clear_token_method_of_db_user_manipulator_with_a_user_id(
    db_user_manipulator_with_a_user_id: DBUserManipulator,
) -> None:
    with raises(ValueError, match="A DB user is absent"):
        db_user_manipulator_with_a_user_id.clear_token()


def test_a_clear_token_method_of_db_user_manipulator_with_a_db_user(
    db_user_manipulator_with_a_db_user: DBUserManipulator,
) -> None:
    db_user_manipulator_with_a_db_user.clear_token()
