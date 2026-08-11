import pytest

from disco_client import DiscoAPIError, TrackNotFoundError
from disco_shared.models.track_upload import TrackUpload


def test_full_track_lifecycle_over_real_http(client, tmp_path):
    file_path = tmp_path / "song.mp3"
    file_bytes = b"fake audio bytes"
    file_path.write_bytes(file_bytes)

    track_id = client.tracks.upload_track(file_path, TrackUpload(name="Original", cue_point=5))

    details = client.tracks.get_track(track_id)
    assert details.name == "Original"
    assert details.cue_point == 5

    # the uploaded file itself round-trips correctly - a different response
    # shape (raw bytes) than every other endpoint here (JSON), worth proving
    # for real rather than assuming it works because the JSON ones do.
    assert client.tracks.get_track_file(track_id) == file_bytes

    update = details.for_update()
    update.name = "Renamed"
    update.cue_point = None
    client.tracks.update_track(track_id, update)

    updated = client.tracks.get_track(track_id)
    assert updated.name == "Renamed"
    assert updated.cue_point is None
    assert updated.path == details.path  # untouched fields survive the update

    assert any(t.id == track_id for t in client.tracks.list_tracks())

    client.tracks.delete_track(track_id)

    with pytest.raises(TrackNotFoundError):
        client.tracks.get_track(track_id)


def test_get_track_raises_track_not_found_for_a_real_missing_track(client):
    with pytest.raises(TrackNotFoundError):
        client.tracks.get_track(999)


def test_list_tracks_reflects_multiple_real_uploads(client, tmp_path):
    file_path = tmp_path / "song.mp3"
    file_path.write_bytes(b"fake audio bytes")

    first_id = client.tracks.upload_track(file_path, TrackUpload(name="First", cue_point=1))
    second_id = client.tracks.upload_track(file_path, TrackUpload(name="Second", cue_point=2))

    tracks = {t.id: t.name for t in client.tracks.list_tracks()}

    assert tracks == {first_id: "First", second_id: "Second"}


def test_upload_track_raises_disco_api_error_for_a_real_unsupported_format(client, tmp_path):
    file_path = tmp_path / "notes.txt"
    file_path.write_text("not an audio file")

    with pytest.raises(DiscoAPIError) as exc_info:
        client.tracks.upload_track(file_path, TrackUpload(name="Bad", cue_point=1))

    assert exc_info.value.status_code == 400
    assert exc_info.value.message == "File format not supported"
