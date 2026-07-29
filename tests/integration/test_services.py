import pytest

from disco_server import create_app, services
from disco_server.core.models.track import Track
from disco_server.core.services.track_library import TrackLibrary


@pytest.fixture
def app(tmp_path):
    """A Flask app wired to a fresh, initialised database."""
    app = create_app({"DATABASE_PATH": str(tmp_path / "test.db")})
    app.database.init_db()
    return app


def test_get_track_library_returns_the_same_instance_within_an_app(app):
    with app.app_context():
        first = services.get_track_library()
        second = services.get_track_library()

    assert isinstance(first, TrackLibrary)
    assert first is second


def test_get_boombox_returns_the_same_instance_within_an_app(app, monkeypatch):
    class FakeBoombox:
        pass

    monkeypatch.setattr(services, "Boombox", FakeBoombox)

    with app.app_context():
        first = services.get_boombox()
        second = services.get_boombox()

    assert isinstance(first, FakeBoombox)
    assert first is second


def test_tracks_endpoint_lists_tracks_from_the_injected_library(app):
    with app.app_context():
        services.get_track_library().create_track(Track(name="song1", path="/music/song1.mp3", cue_time=5))

    response = app.test_client().get("/tracks")

    assert response.status_code == 200
    assert response.get_json() == ["song1"]
