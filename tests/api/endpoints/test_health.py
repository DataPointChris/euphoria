import pytest

from ichrisbirch import __version__
from ichrisbirch.api.endpoints import health
from tests.helpers import endpoint

ENDPOINT = 'health'


@pytest.fixture(scope='module')
def router():
    return health.router


def test_health_check_version(test_app):
    """Test if the version provided by health check matches project version"""
    response = test_app.get(endpoint(ENDPOINT))
    assert response.status_code == 200
    assert response.json()['version'] == __version__