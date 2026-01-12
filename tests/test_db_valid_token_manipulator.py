from collections.abc import Callable
from typing import Any
from unittest.mock import MagicMock, patch

from pytest import fixture
from sqlalchemy import Result, Select
from sqlalchemy.orm import Session

from libs import DBValidTokenManipulator, ValidToken

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
def db_valid_token_manipulator(
    db_session_mock: Session,
) -> DBValidTokenManipulator:
    token = "0123456789abcdef"
    return DBValidTokenManipulator(db_session_mock, token)


@patch(
    "libs.db_valid_token_manipulator.select",
    return_value=select_instance_mock,
)
@patch(
    "libs.db_valid_token_manipulator.ValidToken",
    spec=ValidToken,
)
def test_a_get_method_of_db_valid_token_manipulator(
    db_valid_token_mock: ValidToken,  # pyright: ignore[reportUnusedParameter]  # type: ignore
    select_function_mock: Callable[  # pyright: ignore[reportUnusedParameter]  # type: ignore
        ...,
        Select[
            tuple[
                Any, ...  # pyright: ignore[reportExplicitAny]  # type: ignore
            ]
        ],
    ],
    db_valid_token_manipulator: DBValidTokenManipulator,
) -> None:
    db_valid_token: ValidToken | None = db_valid_token_manipulator.get()

    assert isinstance(db_valid_token, ValidToken)


def test_a_create_method_of_db_valid_token_manipulator(
    db_valid_token_manipulator: DBValidTokenManipulator,
) -> None:
    db_valid_token: ValidToken = db_valid_token_manipulator.create()

    assert isinstance(db_valid_token, ValidToken)
