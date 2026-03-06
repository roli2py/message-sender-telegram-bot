import pytest
from pytest_mock import MockerFixture
from sqlalchemy.orm import Session, sessionmaker


@pytest.fixture
def compiled_session_mock(
    mocker: MockerFixture,
) -> sessionmaker[Session]:
    sessionmaker_mock = mocker.patch(
        "sqlalchemy.orm.sessionmaker",
        autospec=True,
    )
    compiled_session_mock: sessionmaker[Session] = sessionmaker_mock()
    return compiled_session_mock
