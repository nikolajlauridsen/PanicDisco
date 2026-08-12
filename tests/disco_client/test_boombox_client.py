import pytest

from disco_client import BoomboxNotLoadedError, TrackNotFoundError


def test_load_succeeds_on_200(client, requests_mock):
    requests_mock.put(f"{client.base_url}/api/boombox/load/1", status_code=200)

    client.boombox.load(1)


def test_load_raises_track_not_found_on_404(client, requests_mock):
    requests_mock.put(
        f"{client.base_url}/api/boombox/load/1",
        status_code=404,
        json={"error": "Track not found", "status_code": 404},
    )

    with pytest.raises(TrackNotFoundError):
        client.boombox.load(1)


def test_play_succeeds_on_200(client, requests_mock):
    requests_mock.put(f"{client.base_url}/api/boombox/play", status_code=200)

    client.boombox.play()


def test_play_raises_boombox_not_loaded_on_503(client, requests_mock):
    requests_mock.put(
        f"{client.base_url}/api/boombox/play",
        status_code=503,
        json={"error": "No track is loaded", "status_code": 503},
    )

    with pytest.raises(BoomboxNotLoadedError):
        client.boombox.play()


def test_stop_succeeds_on_200(client, requests_mock):
    requests_mock.put(f"{client.base_url}/api/boombox/stop", status_code=200)

    client.boombox.stop()


def test_stop_raises_boombox_not_loaded_on_503(client, requests_mock):
    requests_mock.put(
        f"{client.base_url}/api/boombox/stop",
        status_code=503,
        json={"error": "No track is loaded", "status_code": 503},
    )

    with pytest.raises(BoomboxNotLoadedError):
        client.boombox.stop()


def test_pause_succeeds_on_200(client, requests_mock):
    requests_mock.put(f"{client.base_url}/api/boombox/pause", status_code=200)

    client.boombox.pause()


def test_pause_raises_boombox_not_loaded_on_503(client, requests_mock):
    requests_mock.put(
        f"{client.base_url}/api/boombox/pause",
        status_code=503,
        json={"error": "No track is loaded", "status_code": 503},
    )

    with pytest.raises(BoomboxNotLoadedError):
        client.boombox.pause()


def test_resume_succeeds_on_200(client, requests_mock):
    requests_mock.put(f"{client.base_url}/api/boombox/resume", status_code=200)

    client.boombox.resume()


def test_resume_raises_boombox_not_loaded_on_503(client, requests_mock):
    requests_mock.put(
        f"{client.base_url}/api/boombox/resume",
        status_code=503,
        json={"error": "No track is loaded", "status_code": 503},
    )

    with pytest.raises(BoomboxNotLoadedError):
        client.boombox.resume()
