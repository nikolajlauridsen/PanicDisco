import pytest

from disco_server import create_app, services
from disco_core.models.track import Track


class FakeBoombox:
    """A fake Boombox that records calls instead of touching real VLC."""

    def __init__(self, vlc_args=''):
        self.loaded_track = None
        self.calls = []

    def is_loaded(self):
        return self.loaded_track is not None

    def load_track(self, track):
        self.loaded_track = track
        self.calls.append(("load_track", track))

    def play(self):
        self.calls.append(("play",))

    def stop(self):
        self.calls.append(("stop",))

    def pause(self):
        self.calls.append(("pause",))

    def resume(self):
        self.calls.append(("resume",))


@pytest.fixture
def app(tmp_path, monkeypatch):
    """A Flask app wired to a fresh, initialised database, with a fake Boombox."""
    monkeypatch.setattr(services, "Boombox", FakeBoombox)

    app = create_app({"DATABASE_PATH": str(tmp_path / "test.db")})
    app.database.init_db()
    return app


def load_boombox(app):
    """Return the app's cached (fake) Boombox instance, creating it if needed."""
    with app.app_context():
        return services.get_boombox()


def test_load_track_endpoint_loads_track_and_returns_200(app):
    with app.app_context():
        services.get_track_library().create_track(Track(name="song1", path="/music/song1.mp3", cue_time=5))
        track_id = services.get_track_library().get_tracks()[0].id

    response = app.test_client().put(f"/api/boombox/load/{track_id}")

    assert response.status_code == 200

    boombox = load_boombox(app)
    assert boombox.loaded_track.id == track_id
    assert boombox.loaded_track.name == "song1"


def test_load_track_endpoint_returns_404_when_track_missing(app):
    response = app.test_client().put("/api/boombox/load/9999")

    assert response.status_code == 404
    assert response.get_json() == {"error": "Track not found", "status_code": 404}


def test_play_endpoint_starts_playback_and_returns_200(app):
    boombox = load_boombox(app)
    boombox.load_track(Track(id=1, name="song1", path="/music/song1.mp3", cue_time=5))

    response = app.test_client().put("/api/boombox/play")

    assert response.status_code == 200
    assert ("play",) in boombox.calls


def test_play_endpoint_returns_503_when_not_loaded(app):
    response = app.test_client().put("/api/boombox/play")

    assert response.status_code == 503
    assert response.get_json() == {"error": "Track not loaded", "status_code": 503}


def test_stop_endpoint_stops_playback_and_returns_200(app):
    boombox = load_boombox(app)
    boombox.load_track(Track(id=1, name="song1", path="/music/song1.mp3", cue_time=5))

    response = app.test_client().put("/api/boombox/stop")

    assert response.status_code == 200
    assert ("stop",) in boombox.calls


def test_stop_endpoint_returns_503_when_not_loaded(app):
    response = app.test_client().put("/api/boombox/stop")

    assert response.status_code == 503
    assert response.get_json() == {"error": "Track not loaded", "status_code": 503}


def test_pause_endpoint_pauses_playback_and_returns_200(app):
    boombox = load_boombox(app)
    boombox.load_track(Track(id=1, name="song1", path="/music/song1.mp3", cue_time=5))

    response = app.test_client().put("/api/boombox/pause")

    assert response.status_code == 200
    assert ("pause",) in boombox.calls


def test_pause_endpoint_returns_503_when_not_loaded(app):
    response = app.test_client().put("/api/boombox/pause")

    assert response.status_code == 503
    assert response.get_json() == {"error": "Track not loaded", "status_code": 503}


def test_resume_endpoint_resumes_playback_and_returns_200(app):
    boombox = load_boombox(app)
    boombox.load_track(Track(id=1, name="song1", path="/music/song1.mp3", cue_time=5))

    response = app.test_client().put("/api/boombox/resume")

    assert response.status_code == 200
    assert ("resume",) in boombox.calls


def test_resume_endpoint_returns_503_when_not_loaded(app):
    response = app.test_client().put("/api/boombox/resume")

    assert response.status_code == 503
    assert response.get_json() == {"error": "Track not loaded", "status_code": 503}
