import pytest
from api_test_utils.api_test_session_config import APITestSessionConfig
from api_test_utils.fixtures import api_client   # pylint: disable=unused-import


@pytest.fixture(scope='session')
def api_test_config() -> APITestSessionConfig:

    return APITestSessionConfig()
