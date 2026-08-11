import pytest

from disco_client import TrackNotFoundError
from disco_shared.models.track_upload import TrackUpload


def test_full_track_lifecycle_over_real_http(client, tmp_path):
    file_path = tmp_path / "song.mp3"
    file_path.write_bytes(b"fake audio bytes")

    track_id = client.tracks.upload_track(file_path, TrackUpload(name="Original", cue_point=5))

    details = client.tracks.get_track(track_id)
    assert details.name == "Original"
    assert details.cue_point == 5

    update = details.for_update()
    update.name = "Renamed"
    update.cue_point = None
    client.tracks.update_track(track_id, update)

    updated = client.tracks.get_track(track_id)
    assert updated.name == "Renamed"
    assert updated.cue_point is None

    assert any(t.id == track_id for t in client.tracks.list_tracks())

    client.tracks.delete_track(track_id)

    with pytest.raises(TrackNotFoundError):
        client.tracks.get_track(track_id)


def test_get_track_raises_track_not_found_for_a_real_missing_track(client):
    with pytest.raises(TrackNotFoundError):
        client.tracks.get_track(999)
