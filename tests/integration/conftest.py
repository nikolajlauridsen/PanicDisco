import pytest

from disco_server.core.database.database import Database
from disco_server.core.models.track import Track
from disco_server.core.services.track_library import TrackLibrary


@pytest.fixture
def db_path(tmp_path):
    """Path to a fresh per-test SQLite file, shared by any Database pointed at it."""
    return str(tmp_path / "test.db")


@pytest.fixture
def database(db_path):
    """A real SQLite database backed by a fresh per-test file."""
    db = Database(db_path=db_path)
    db.init_db()
    return db


@pytest.fixture
def library(database):
    """A TrackLibrary wired to an empty, initialised database."""
    return TrackLibrary(database)


@pytest.fixture
def make_track():
    """Factory for Track objects with sensible defaults.

    New tracks default to ``id=None`` since the database assigns the id.
    """
    def _make(name="song", path=None, cue_time=50, id=None):
        return Track(
            name=name,
            path=path if path is not None else f"/music/{name}.mp3",
            cue_time=cue_time,
            id=id,
        )
    return _make
