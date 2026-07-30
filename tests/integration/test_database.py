"""Integration tests for Database against a real SQLite database."""

from disco_server.core.database.database import Database


def test_get_track_returns_none_when_missing(database):
    assert database.get_track(9999) is None


def test_get_track_returns_the_matching_track(database, make_track):
    track = database.add_track(make_track(name="song1", path="/music/song1.mp3", cue_time=42))

    fetched = database.get_track(track.id)

    assert fetched.id == track.id
    assert fetched.name == "song1"
    assert fetched.path == "/music/song1.mp3"
    assert fetched.cue_time == 42


def test_get_track_returns_the_matching_track_when_names_duplicated(database, make_track):
    """Names aren't unique, so get_track must key off id."""
    first = database.add_track(make_track(name="dup", path="/music/first.mp3"))
    second = database.add_track(make_track(name="dup", path="/music/second.mp3"))

    assert database.get_track(first.id).path == "/music/first.mp3"
    assert database.get_track(second.id).path == "/music/second.mp3"


def test_get_track_reads_tracks_persisted_by_a_different_database_instance(database, make_track, db_path):
    """Simulates an app restart: a brand new Database/engine/session opening
    the same file, rather than reading through the same session that wrote it.
    """
    track = database.add_track(make_track(name="song1", path="/music/song1.mp3", cue_time=7))

    reopened = Database(db_path=db_path)
    fetched = reopened.get_track(track.id)

    assert fetched is not None
    assert fetched.path == "/music/song1.mp3"
    assert fetched.cue_time == 7


def test_add_track_result_is_readable_after_session_is_torn_down(database, make_track):
    """Regression test for DetachedInstanceError: Database must hand back a
    plain domain Track with no SQLAlchemy session ties, so attribute reads
    must never depend on the originating session still being alive (e.g.
    after another thread's scoped_session.remove(), or a request-scoped
    session ending).
    """
    track = database.add_track(make_track(name="song1", cue_time=5))

    database.db_sessions.remove()

    assert track.name == "song1"
    assert track.cue_time == 5


def test_get_track_result_is_readable_after_session_is_torn_down(database, make_track):
    track = database.add_track(make_track(name="song1", cue_time=5))

    fetched = database.get_track(track.id)
    database.db_sessions.remove()

    assert fetched.name == "song1"
    assert fetched.cue_time == 5
