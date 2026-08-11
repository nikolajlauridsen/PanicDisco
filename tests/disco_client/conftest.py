import pytest

from disco_client import DiscoClient


@pytest.fixture
def client():
    """A DiscoClient pointed at a fake base URL, for use with requests_mock."""
    return DiscoClient("http://disco-server.test")
