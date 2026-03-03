from unittest.mock import patch

import pytest
from sqlalchemy.orm import Session, sessionmaker


@pytest.fixture
@patch("sqlalchemy.orm.sessionmaker", autospec=True)
def compiled_session_mock(
    sessionmaker_mock: type[sessionmaker],
) -> sessionmaker[Session]:
    compiled_session_mock: sessionmaker[Session] = sessionmaker_mock()
    return compiled_session_mock
