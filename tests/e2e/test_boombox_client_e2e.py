import pytest

from disco_client import BoomboxNotLoadedError, TrackNotFoundError
from disco_shared.models.track_upload import TrackUpload


@pytest.fixture
def track_id(client, tmp_path):
    file_path = tmp_path / "song.mp3"
    file_path.write_bytes(b"fake audio bytes")
    return client.tracks.upload_track(file_path, TrackUpload(name="Cued", cue_point=5))


def test_full_boombox_lifecycle_over_real_http(client, track_id):
    client.boombox.load(track_id)

    # real VLC underneath - proves the client's calls actually reach a real
    # Boombox, not just that the server returns 200.
    client.boombox.play()
    client.boombox.pause()
    client.boombox.resume()
    client.boombox.stop()


def test_load_raises_track_not_found_for_a_real_missing_track(client):
    with pytest.raises(TrackNotFoundError):
        client.boombox.load(999)


def test_play_raises_boombox_not_loaded_for_a_real_unloaded_boombox(client):
    with pytest.raises(BoomboxNotLoadedError):
        client.boombox.play()
