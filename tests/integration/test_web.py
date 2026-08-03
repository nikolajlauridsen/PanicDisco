import pytest

from disco_server import create_app, services
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
