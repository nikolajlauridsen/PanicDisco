"""Integration tests for Database's key-value store against a real SQLite
database.

The functionality lives on Database rather than a dedicated class for now,
but the tests are kept separate to track that concern independently of the
track-related Database tests in test_database.py.
"""

from disco_server.core.database.database import Database


def test_get_value_returns_none_when_missing(database):
    assert database.get_value("missing") is None


def test_set_value_then_get_value_returns_the_value(database):
    database.set_value("last_loaded_track_id", "42")

    assert database.get_value("last_loaded_track_id") == "42"


def test_set_value_overwrites_the_existing_value_for_the_same_key(database):
    """set_value must upsert (update if the key already exists), not insert a
    second row — the key column is unique, so a plain insert-on-every-call
    would violate that constraint on the second write.
    """
    database.set_value("last_loaded_track_id", "42")
    database.set_value("last_loaded_track_id", "7")

    assert database.get_value("last_loaded_track_id") == "7"


def test_set_value_does_not_affect_other_keys(database):
    database.set_value("a", "1")
    database.set_value("b", "2")

    assert database.get_value("a") == "1"
    assert database.get_value("b") == "2"


def test_get_value_reads_a_value_persisted_by_a_different_database_instance(database, db_path):
    """Simulates an app restart: a brand new Database/engine/session opening
    the same file, rather than reading through the same session that wrote it.
    """
    database.set_value("last_loaded_track_id", "42")

    reopened = Database(db_path=db_path)

    assert reopened.get_value("last_loaded_track_id") == "42"


def test_get_value_result_is_readable_after_session_is_torn_down(database):
    """Regression test for DetachedInstanceError, same concern as the track
    equivalent in test_database.py: get_value must hand back a plain str, not
    something tied to the session that read it.
    """
    database.set_value("last_loaded_track_id", "42")

    database.db_sessions.remove()

    assert database.get_value("last_loaded_track_id") == "42"
