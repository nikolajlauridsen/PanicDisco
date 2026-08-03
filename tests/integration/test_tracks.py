import io

import pytest

from disco_server import create_app, services
from disco_server.core.models.track import Track
from disco_server.core.services import file_manager


@pytest.fixture
def app(tmp_path):
    """A Flask app wired to a fresh, initialised database."""
    app = create_app({
        "DATABASE_PATH": str(tmp_path / "test.db"),
        "UPLOAD_FOLDER": str(tmp_path / "uploads"),
    })
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


def test_get_track_file_endpoint_serves_the_uploaded_file(app):
    upload_folder = app.config["UPLOAD_FOLDER"]
    file_path = f"{upload_folder}/song1.mp3"
    with open(file_path, "wb") as f:
        f.write(b"fake mp3 bytes")

    with app.app_context():
        services.get_track_library().create_track(Track(name="song1", path=file_path, cue_time=5))
        track_id = services.get_track_library().get_tracks()[0].id

    response = app.test_client().get(f"/api/tracks/{track_id}/file")

    assert response.status_code == 200
    assert response.data == b"fake mp3 bytes"


def test_get_track_file_endpoint_returns_404_when_track_missing(app):
    response = app.test_client().get("/api/tracks/9999/file")

    assert response.status_code == 404
    assert response.get_json() == {"error": "Track not found", "status_code": 404}


def test_get_track_file_endpoint_returns_404_when_path_is_outside_the_upload_folder(app):
    with app.app_context():
        services.get_track_library().create_track(Track(name="song1", path="/music/song1.mp3", cue_time=5))
        track_id = services.get_track_library().get_tracks()[0].id

    response = app.test_client().get(f"/api/tracks/{track_id}/file")

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


def test_upload_track_endpoint_creates_track_and_returns_201(app, monkeypatch):
    saved = []
    monkeypatch.setattr(file_manager, "save", lambda file, path: saved.append((file.filename, path)))

    response = app.test_client().post(
        "/api/tracks/upload",
        data={
            "file": (io.BytesIO(b"fake mp3 bytes"), "song1.mp3"),
            "name": "song1",
            "cue_point": "5",
        },
        content_type="multipart/form-data",
    )

    assert response.status_code == 201
    assert len(saved) == 1
    saved_filename, saved_path = saved[0]
    assert saved_filename == "song1.mp3"
    assert saved_path.startswith(app.config["UPLOAD_FOLDER"])
    assert saved_path.endswith(".mp3")

    with app.app_context():
        tracks = services.get_track_library().get_tracks()

    assert len(tracks) == 1
    created_track = tracks[0]
    assert created_track.name == "song1"
    assert created_track.cue_time == 5
    assert created_track.path == saved_path
    assert response.headers["Location"] == f"/api/tracks/{created_track.id}"


def test_upload_track_endpoint_returns_400_for_unsupported_format(app, monkeypatch):
    saved = []
    monkeypatch.setattr(file_manager, "save", lambda file, path: saved.append(path))

    response = app.test_client().post(
        "/api/tracks/upload",
        data={
            "file": (io.BytesIO(b"not audio"), "notes.txt"),
            "name": "song1",
            "cue_point": "5",
        },
        content_type="multipart/form-data",
    )

    assert response.status_code == 400
    assert response.get_json() == {"error": "File format not supported", "status_code": 400}
    assert saved == []

    with app.app_context():
        assert services.get_track_library().get_tracks() == []


@pytest.mark.parametrize("extension", ["mp3", "wav", "flac"])
def test_upload_track_endpoint_accepts_all_supported_formats(app, monkeypatch, extension):
    saved = []
    monkeypatch.setattr(file_manager, "save", lambda file, path: saved.append(path))

    response = app.test_client().post(
        "/api/tracks/upload",
        data={
            "file": (io.BytesIO(b"fake audio bytes"), f"song1.{extension}"),
            "name": "song1",
            "cue_point": "5",
        },
        content_type="multipart/form-data",
    )

    assert response.status_code == 201
    assert len(saved) == 1
    assert saved[0].endswith(f".{extension}")


def test_upload_track_endpoint_returns_400_when_file_missing(app, monkeypatch):
    saved = []
    monkeypatch.setattr(file_manager, "save", lambda file, path: saved.append(path))

    response = app.test_client().post(
        "/api/tracks/upload",
        data={"name": "song1", "cue_point": "5"},
        content_type="multipart/form-data",
    )

    assert response.status_code == 400
    assert response.get_json() == {"error": "No file uploaded", "status_code": 400}
    assert saved == []

    with app.app_context():
        assert services.get_track_library().get_tracks() == []


def test_upload_track_endpoint_returns_400_for_invalid_metadata(app, monkeypatch):
    saved = []
    monkeypatch.setattr(file_manager, "save", lambda file, path: saved.append(path))

    response = app.test_client().post(
        "/api/tracks/upload",
        data={
            "file": (io.BytesIO(b"fake mp3 bytes"), "song1.mp3"),
            "name": "song1",
            "cue_point": "not-a-number",
        },
        content_type="multipart/form-data",
    )

    assert response.status_code == 400
    assert response.get_json() == {"error": "Invalid track metadata", "status_code": 400}
    assert saved == []

    with app.app_context():
        assert services.get_track_library().get_tracks() == []
