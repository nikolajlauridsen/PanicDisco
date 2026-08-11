import pytest

from disco_client import BoomboxNotLoadedError, DiscoAPIError, TrackNotFoundError
from disco_client.clients.client_base import ClientBase

BASE_URL = "http://disco-server.test"


@pytest.fixture
def base_client():
    return ClientBase(None, BASE_URL, timeout=5)


def test_raise_for_status_does_nothing_on_2xx(base_client, requests_mock):
    requests_mock.get(BASE_URL, status_code=200)
    response = base_client.session.get(BASE_URL)

    base_client._raise_for_status(response)


def test_raise_for_status_raises_track_not_found_on_404(base_client, requests_mock):
    requests_mock.get(BASE_URL, status_code=404, json={"error": "Track not found", "status_code": 404})
    response = base_client.session.get(BASE_URL)

    with pytest.raises(TrackNotFoundError) as exc_info:
        base_client._raise_for_status(response)
    assert exc_info.value.status_code == 404
    assert exc_info.value.message == "Track not found"


def test_raise_for_status_raises_boombox_not_loaded_on_503(base_client, requests_mock):
    requests_mock.get(BASE_URL, status_code=503, json={"error": "Track not loaded", "status_code": 503})
    response = base_client.session.get(BASE_URL)

    with pytest.raises(BoomboxNotLoadedError) as exc_info:
        base_client._raise_for_status(response)
    assert exc_info.value.status_code == 503
    assert exc_info.value.message == "Track not loaded"


def test_raise_for_status_raises_generic_disco_api_error_on_other_codes(base_client, requests_mock):
    requests_mock.get(BASE_URL, status_code=500, json={"error": "Something broke", "status_code": 500})
    response = base_client.session.get(BASE_URL)

    with pytest.raises(DiscoAPIError) as exc_info:
        base_client._raise_for_status(response)
    assert exc_info.value.status_code == 500
    assert exc_info.value.message == "Something broke"


def test_raise_for_status_falls_back_to_reason_when_body_is_not_json(base_client, requests_mock):
    requests_mock.get(BASE_URL, status_code=500, text="not json", reason="Internal Server Error")
    response = base_client.session.get(BASE_URL)

    with pytest.raises(DiscoAPIError) as exc_info:
        base_client._raise_for_status(response)
    assert exc_info.value.message == "Internal Server Error"
