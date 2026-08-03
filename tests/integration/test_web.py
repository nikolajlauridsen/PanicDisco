import pytest

from disco_server import create_app, services
from disco_server.blueprints.web import format_cue_point
from disco_server.core.models.track import Track


@pytest.fixture
def app(tmp_path):
    """A Flask app wired to a fresh, initialised database."""
    app = create_app({
        "DATABASE_PATH": str(tmp_path / "test.db"),
        "UPLOAD_FOLDER": str(tmp_path / "uploads"),
    })
    app.database.init_db()
    return app


def test_index_page_lists_tracks_from_the_injected_library(app):
    with app.app_context():
        services.get_track_library().create_track(Track(name="song1", path="/music/song1.mp3", cue_time=5))

    response = app.test_client().get("/")

    assert response.status_code == 200
    assert b"song1" in response.data


def test_index_page_renders_a_preview_button_pointing_at_the_track_file(app):
    with app.app_context():
        services.get_track_library().create_track(Track(name="song1", path="/music/song1.mp3", cue_time=5))
        track_id = services.get_track_library().get_tracks()[0].id

    response = app.test_client().get("/")
    body = response.get_data(as_text=True)

    assert response.status_code == 200
    assert f'data-src="/api/tracks/{track_id}/file"' in body
    assert 'data-cue-point="5"' in body
    assert "preview-toggle" in body
    assert "Play" in body


def test_index_page_renders_a_delete_button_pointing_at_the_track(app):
    with app.app_context():
        services.get_track_library().create_track(Track(name="song1", path="/music/song1.mp3", cue_time=5))
        track_id = services.get_track_library().get_tracks()[0].id

    response = app.test_client().get("/")
    body = response.get_data(as_text=True)

    assert response.status_code == 200
    assert f'data-delete-url="/api/tracks/{track_id}"' in body
    assert 'data-name="song1"' in body
    assert "track-delete" in body


def test_index_page_renders_zero_cue_point_when_track_has_none(app):
    with app.app_context():
        services.get_track_library().create_track(Track(name="song1", path="/music/song1.mp3", cue_time=None))

    response = app.test_client().get("/")
    body = response.get_data(as_text=True)

    assert response.status_code == 200
    assert 'data-cue-point="0"' in body


def test_tracks_js_is_served_as_a_static_file(app):
    response = app.test_client().get("/static/js/tracks.js")

    assert response.status_code == 200
    assert b"preview-toggle" in response.data
    assert b"track-delete" in response.data
    assert b"edit-save" in response.data
    assert b"PUT" in response.data


def test_index_page_renders_an_edit_button_and_accordion_row(app):
    with app.app_context():
        services.get_track_library().create_track(Track(name="song1", path="/music/song1.mp3", cue_time=5))
        track_id = services.get_track_library().get_tracks()[0].id

    response = app.test_client().get("/")
    body = response.get_data(as_text=True)

    assert response.status_code == 200
    assert f'data-update-url="/api/tracks/{track_id}"' in body
    assert "track-edit" in body
    assert 'class="edit-row hidden"' in body
    assert f'data-path="/music/song1.mp3"' in body
    assert 'value="song1"' in body
    assert f'src="/api/tracks/{track_id}/file"' in body


def test_index_page_renders_cue_point_as_minutes_seconds(app):
    with app.app_context():
        services.get_track_library().create_track(Track(name="song1", path="/music/song1.mp3", cue_time=65))

    response = app.test_client().get("/")

    assert response.status_code == 200
    assert "1:05" in response.get_data(as_text=True)


def test_format_cue_point_pads_seconds_under_ten():
    assert format_cue_point(65) == "1:05"


def test_format_cue_point_handles_under_a_minute():
    assert format_cue_point(5) == "0:05"


def test_format_cue_point_handles_none():
    assert format_cue_point(None) == "—"


def test_upload_page_renders(app):
    response = app.test_client().get("/upload")

    assert response.status_code == 200


def test_upload_page_renders_the_drop_zone_and_form_fields(app):
    response = app.test_client().get("/upload")
    body = response.get_data(as_text=True)

    assert 'id="drop-zone"' in body
    assert 'accept=".mp3,.wav,.flac,audio/*"' in body
    assert 'id="name-input"' in body
    assert 'id="cue-point-input"' in body
    assert 'id="mark-cue-btn"' in body
    assert 'id="submit-btn"' in body
    assert 'data-upload-url="/api/tracks/upload"' in body


def test_upload_js_is_served_as_a_static_file(app):
    response = app.test_client().get("/static/js/upload.js")

    assert response.status_code == 200
    assert b"FormData" in response.data
    assert b"handleFileSelected" in response.data
