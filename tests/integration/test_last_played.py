"""Integration tests for LastPlayed against a real SQLite database.

LastPlayed resolves the stored track id via Database.get_track() directly
(not services.get_track_library()), so these are plain Database-backed
tests like test_database.py/test_key_value.py — no Flask app/app_context
needed.
"""

import pytest

from disco_server.core.database.database import Database
from disco_server.core.services.last_played import LastPlayed


@pytest.fixture
def last_played(database):
    return LastPlayed(database)


def test_get_returns_none_when_nothing_has_been_set(last_played):
    assert last_played.get() is None


def test_set_then_get_returns_the_track(last_played, database, make_track):
    track = database.add_track(make_track(name="song1", path="/music/song1.mp3", cue_time=42))

    last_played.set(track)
    fetched = last_played.get()

    assert fetched is not None
    assert fetched.id == track.id
    assert fetched.name == "song1"
    assert fetched.path == "/music/song1.mp3"
    assert fetched.cue_time == 42


def test_set_raises_when_track_has_no_id(last_played, make_track):
    """A track that's never been added to the database has no id yet, so
    there's nothing valid to record — set() must fail loudly rather than
    persisting a value get() can never resolve back to a track.
    """
    track = make_track(name="song1", id=None)

    with pytest.raises(RuntimeError):
        last_played.set(track)


def test_set_overwrites_the_previously_recorded_track(last_played, database, make_track):
    first = database.add_track(make_track(name="song1"))
    second = database.add_track(make_track(name="song2"))

    last_played.set(first)
    last_played.set(second)

    assert last_played.get().id == second.id


def test_get_returns_none_when_the_recorded_track_has_since_been_deleted(last_played, database, make_track):
    """The stored id can point at a track that no longer exists (deleted
    after it was last played) — get() must report nothing, not raise.
    """
    track = database.add_track(make_track(name="song1"))
    last_played.set(track)

    database.remove_track(track)

    assert last_played.get() is None


def test_set_persists_across_a_fresh_database_instance_on_the_same_file(database, make_track, db_path):
    """Simulates an app restart: a brand new Database/engine/session opening
    the same file, rather than reading through the same session that wrote it.
    """
    track = database.add_track(make_track(name="song1", path="/music/song1.mp3"))
    LastPlayed(database).set(track)

    reopened = LastPlayed(Database(db_path=db_path))
    fetched = reopened.get()

    assert fetched is not None
    assert fetched.id == track.id
    assert fetched.path == "/music/song1.mp3"
