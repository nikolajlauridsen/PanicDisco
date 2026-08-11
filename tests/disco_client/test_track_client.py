import pytest

from disco_client import DiscoAPIError, TrackNotFoundError
from disco_shared.models.track_details import TrackDetails
from disco_shared.models.track_entity import TrackEntity
from disco_shared.models.track_update import TrackUpdate
from disco_shared.models.track_upload import TrackUpload


def test_list_tracks_returns_track_entities(client, requests_mock):
    requests_mock.get(
        f"{client.base_url}/api/tracks",
        json=[{"id": 1, "name": "song1"}, {"id": 2, "name": "song2"}],
    )

    tracks = client.tracks.list_tracks()

    assert tracks == [TrackEntity(id=1, name="song1"), TrackEntity(id=2, name="song2")]


def test_get_track_returns_track_details(client, requests_mock):
    requests_mock.get(
        f"{client.base_url}/api/tracks/1",
        json={"id": 1, "name": "song1", "cue_point": 5, "path": "/music/song1.mp3"},
    )

    track = client.tracks.get_track(1)

    assert track == TrackDetails(id=1, name="song1", cue_point=5, path="/music/song1.mp3")


def test_get_track_raises_track_not_found_on_404(client, requests_mock):
    requests_mock.get(
        f"{client.base_url}/api/tracks/1",
        status_code=404,
        json={"error": "Track not found", "status_code": 404},
    )

    with pytest.raises(TrackNotFoundError):
        client.tracks.get_track(1)


def test_get_track_file_returns_the_raw_bytes(client, requests_mock):
    requests_mock.get(f"{client.base_url}/api/tracks/1/file", content=b"fake audio bytes")

    assert client.tracks.get_track_file(1) == b"fake audio bytes"


def test_get_track_file_raises_track_not_found_on_404(client, requests_mock):
    requests_mock.get(
        f"{client.base_url}/api/tracks/1/file",
        status_code=404,
        json={"error": "Track not found", "status_code": 404},
    )

    with pytest.raises(TrackNotFoundError):
        client.tracks.get_track_file(1)


def test_update_track_sends_the_update_body(client, requests_mock):
    mock = requests_mock.put(f"{client.base_url}/api/tracks/1", status_code=204)

    client.tracks.update_track(1, TrackUpdate(name="renamed", cue_point=10, path="/music/song1.mp3"))

    assert mock.last_request.json() == {"name": "renamed", "cue_point": 10, "path": "/music/song1.mp3"}


def test_update_track_raises_track_not_found_on_404(client, requests_mock):
    requests_mock.put(
        f"{client.base_url}/api/tracks/1",
        status_code=404,
        json={"error": "Track not found", "status_code": 404},
    )

    with pytest.raises(TrackNotFoundError):
        client.tracks.update_track(1, TrackUpdate(name="x", cue_point=1, path="/music/x.mp3"))


def test_delete_track_succeeds_on_204(client, requests_mock):
    requests_mock.delete(f"{client.base_url}/api/tracks/1", status_code=204)

    client.tracks.delete_track(1)


def test_delete_track_raises_track_not_found_on_404(client, requests_mock):
    requests_mock.delete(
        f"{client.base_url}/api/tracks/1",
        status_code=404,
        json={"error": "Track not found", "status_code": 404},
    )

    with pytest.raises(TrackNotFoundError):
        client.tracks.delete_track(1)


def test_upload_track_returns_the_created_id(client, requests_mock, tmp_path):
    file_path = tmp_path / "song.mp3"
    file_path.write_bytes(b"fake audio")
    requests_mock.post(
        f"{client.base_url}/api/tracks/upload",
        status_code=201,
        headers={"Location": "/api/tracks/42"},
    )

    track_id = client.tracks.upload_track(file_path, TrackUpload(name="song", cue_point=5))

    assert track_id == 42


def test_upload_track_sends_the_file_and_metadata_as_multipart(client, requests_mock, tmp_path):
    file_path = tmp_path / "song.mp3"
    file_path.write_bytes(b"fake audio")
    mock = requests_mock.post(
        f"{client.base_url}/api/tracks/upload",
        status_code=201,
        headers={"Location": "/api/tracks/1"},
    )

    client.tracks.upload_track(file_path, TrackUpload(name="song", cue_point=5))

    request = mock.last_request
    assert "multipart/form-data" in request.headers["Content-Type"]
    assert b'name="name"' in request.body
    assert b"song" in request.body
    assert b'filename="song.mp3"' in request.body


def test_upload_track_raises_disco_api_error_on_400(client, requests_mock, tmp_path):
    file_path = tmp_path / "song.mp3"
    file_path.write_bytes(b"fake audio")
    requests_mock.post(
        f"{client.base_url}/api/tracks/upload",
        status_code=400,
        json={"error": "File format not supported", "status_code": 400},
    )

    with pytest.raises(DiscoAPIError) as exc_info:
        client.tracks.upload_track(file_path, TrackUpload(name="song", cue_point=5))

    assert exc_info.value.status_code == 400
    assert exc_info.value.message == "File format not supported"
