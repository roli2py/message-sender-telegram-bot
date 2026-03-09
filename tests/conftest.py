from collections.abc import Generator
from typing import cast

import pytest
from pytest_mock import MockerFixture
from sqlalchemy.orm import Session, sessionmaker


@pytest.fixture
def compiled_session_mock(
    mocker: MockerFixture,
) -> Generator[sessionmaker[Session]]:
    sessionmaker_mock = cast(
        type[sessionmaker],
        mocker.patch(
            "sqlalchemy.orm.sessionmaker",
            autospec=True,
        ),
    )
    compiled_session_mock: sessionmaker[Session] = sessionmaker_mock()
    yield compiled_session_mock
    del compiled_session_mock
