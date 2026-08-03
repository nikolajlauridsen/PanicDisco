import pytest

from disco_server import create_app, services
from disco_server.core.models.track import Track
from disco_server.core.services import file_manager


@pytest.fixture
def app(tmp_path):
    """A Flask app wired to a fresh, initialised database."""
    app = create_app({"DATABASE_PATH": str(tmp_path / "test.db")})
    app.database.init_db()
    return app


def test_tracks_endpoint_lists_tracks_from_the_injected_library(app):
    with app.app_context():
        services.get_track_library().create_track(Track(name="song1", path="/music/song1.mp3", cue_time=5))
        track_id = services.get_track_library().get_tracks()[0].id

    response = app.test_client().get("/api/tracks")

    assert response.status_code == 200
    assert response.get_json() == [{"id": track_id, "name": "song1"}]


def test_get_track_endpoint_returns_track_details(app):
    with app.app_context():
        services.get_track_library().create_track(Track(name="song1", path="/music/song1.mp3", cue_time=5))
        track_id = services.get_track_library().get_tracks()[0].id

    response = app.test_client().get(f"/api/tracks/{track_id}")

    assert response.status_code == 200
    assert response.get_json() == {
        "id": track_id,
        "name": "song1",
        "path": "/music/song1.mp3",
        "cue_point": 5,
    }


def test_get_track_endpoint_returns_404_when_track_missing(app):
    response = app.test_client().get("/api/tracks/9999")

    assert response.status_code == 404
    assert response.get_json() == {"error": "Track not found", "status_code": 404}


def test_update_track_endpoint_updates_track_and_returns_204(app):
    with app.app_context():
        services.get_track_library().create_track(Track(name="song1", path="/music/song1.mp3", cue_time=5))
        track_id = services.get_track_library().get_tracks()[0].id

    response = app.test_client().put(
        f"/api/tracks/{track_id}",
        json={"name": "song2", "path": "/music/song2.mp3", "cue_point": 10},
    )

    assert response.status_code == 204

    with app.app_context():
        updated = services.get_track_library().get_track(track_id)
        assert updated.name == "song2"
        assert updated.path == "/music/song2.mp3"
        assert updated.cue_time == 10


def test_update_track_endpoint_returns_404_when_track_missing(app):
    response = app.test_client().put(
        "/api/tracks/9999",
        json={"name": "song2", "path": "/music/song2.mp3", "cue_point": 10},
    )

    assert response.status_code == 404
    assert response.get_json() == {"error": "Track not found", "status_code": 404}


def test_delete_track_endpoint_removes_track_and_returns_204(app, monkeypatch):
    removed_paths = []
    monkeypatch.setattr(file_manager, "remove", removed_paths.append)

    with app.app_context():
        services.get_track_library().create_track(Track(name="song1", path="/music/song1.mp3", cue_time=5))
        track_id = services.get_track_library().get_tracks()[0].id

    response = app.test_client().delete(f"/api/tracks/{track_id}")

    assert response.status_code == 204
    assert removed_paths == ["/music/song1.mp3"]

    with app.app_context():
        assert services.get_track_library().get_track(track_id) is None


def test_delete_track_endpoint_returns_404_when_track_missing(app):
    response = app.test_client().delete("/api/tracks/9999")

    assert response.status_code == 404
    assert response.get_json() == {"error": "Track not found", "status_code": 404}
