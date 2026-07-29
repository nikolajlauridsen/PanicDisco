"""Integration tests for TrackLibrary against a real SQLite database.

These exercise TrackLibrary end-to-end through the Database layer. To assert
that an operation is actually *persisted*, we build a second TrackLibrary from
the same database and read the state back — TrackLibrary loads its tracks from
the database in ``__init__``, so a fresh instance reflects only what made it to
disk.

The goal is full CRUD backed by the database. Create and Read work today.
Update-persistence and Delete are not implemented yet, so the tests describing
that target behaviour are marked ``xfail`` — they document the remaining work
and will start passing (reported as XPASS) once the gaps are closed.
"""

from disco_server.core.database.database import Database
from disco_server.core.services.track_library import TrackLibrary


def reload(library):
    """Return a fresh TrackLibrary reading from the same database.

    Anything visible here has been persisted, not just held in memory.
    """
    return TrackLibrary(library.database)


def test_fresh_library_is_empty(library):
    assert library.get_tracks() == []


def test_get_track_returns_none_when_missing(library):
    assert library.get_track("does-not-exist") is None


def test_create_track_is_readable_in_memory(library, make_track):
    track = make_track(name="song1")
    library.create_track(track)

    assert library.get_track("song1") is track


def test_create_track_persists_to_database(library, make_track):
    library.create_track(make_track(name="song1", path="/music/song1.mp3", cue_time=42))

    reloaded = reload(library).get_track("song1")

    assert reloaded is not None
    assert reloaded.name == "song1"
    assert reloaded.path == "/music/song1.mp3"
    assert reloaded.cue_time == 42


def test_create_track_assigns_database_id(library, make_track):
    library.create_track(make_track(name="song1", id=None))

    reloaded = reload(library).get_track("song1")

    assert reloaded.id is not None


def test_create_assigns_in_memory_id(library, make_track):
    track = make_track(name="song1")
    library.create_track(track)
    assert library.get_track("song1").id is not None


def test_create_multiple_tracks_persist(library, make_track):
    library.create_track(make_track(name="song1"))
    library.create_track(make_track(name="song2"))
    library.create_track(make_track(name="song3"))

    names = {t.name for t in reload(library).get_tracks()}

    assert names == {"song1", "song2", "song3"}


def test_create_track_with_no_cue_time_persists_as_null(library, make_track):
    library.create_track(make_track(name="song1", cue_time=None))

    reloaded = reload(library).get_track("song1")

    assert reloaded.cue_time is None


def test_create_track_allows_duplicate_names(library, make_track):
    library.create_track(make_track(name="dup", path="/music/first.mp3"))
    library.create_track(make_track(name="dup", path="/music/second.mp3"))

    paths = [t.path for t in reload(library).get_tracks() if t.name == "dup"]

    assert paths == ["/music/first.mp3", "/music/second.mp3"]


def test_track_survives_a_fresh_database_instance_on_the_same_file(library, make_track, db_path):
    """Simulates an app restart: a brand new Database/engine/session opening
    the same file, rather than reading through the same session that wrote it.
    """
    library.create_track(make_track(name="song1", path="/music/song1.mp3", cue_time=7))

    reopened_library = TrackLibrary(Database(db_path=db_path))
    reloaded = reopened_library.get_track("song1")

    assert reloaded is not None
    assert reloaded.path == "/music/song1.mp3"
    assert reloaded.cue_time == 7


def test_update_track_returns_false_when_missing(library, make_track):
    assert library.update_track(9999, make_track(name="nope")) is False


def test_update_track_returns_true_when_present(library, make_track):
    library.create_track(make_track(name="song1"))
    track_id = library.get_track("song1").id

    assert library.update_track(track_id, make_track(name="song1", cue_time=99)) is True


def test_update_track_changes_in_memory_state(library, make_track):
    library.create_track(make_track(name="song1", cue_time=10))
    track_id = library.get_track("song1").id

    library.update_track(track_id, make_track(name="song1", cue_time=99))

    assert library.get_track("song1").cue_time == 99


def test_update_track_persists_to_database(library, make_track):
    library.create_track(make_track(name="song1", cue_time=10))
    track_id = library.get_track("song1").id

    library.update_track(track_id, make_track(name="song1", path="/music/new.mp3", cue_time=99))

    reloaded = reload(library).get_track("song1")

    assert reloaded.cue_time == 99
    assert reloaded.path == "/music/new.mp3"


def test_update_track_updates_only_the_matching_id_when_names_duplicated(library, make_track):
    """Names aren't unique, so update_track must key off id — updating one
    duplicate-named track must not affect the other.
    """
    library.create_track(make_track(name="dup", path="/music/first.mp3", cue_time=1))
    library.create_track(make_track(name="dup", path="/music/second.mp3", cue_time=2))

    dupes = [t for t in library.get_tracks() if t.name == "dup"]
    first_id, second_id = dupes[0].id, dupes[1].id

    library.update_track(second_id, make_track(name="dup", path="/music/updated.mp3", cue_time=99))

    dupes = {t.id: t for t in library.get_tracks() if t.name == "dup"}
    assert dupes[first_id].path == "/music/first.mp3"
    assert dupes[first_id].cue_time == 1
    assert dupes[second_id].path == "/music/updated.mp3"
    assert dupes[second_id].cue_time == 99


def test_delete_track_returns_false_when_not_a_member(library, make_track):
    # Never added to the library, so there is nothing to remove.
    assert library.delete_track(make_track(name="ghost")) is False


def test_delete_track_with_matching_data_but_different_instance_returns_false(library, make_track):
    """delete_track matches by object identity, not by field equality — a
    track built with the same name/path/cue_time as a stored one is still a
    different instance and won't be treated as a member.
    """
    library.create_track(make_track(name="song1", path="/music/a.mp3", cue_time=5))

    lookalike = make_track(name="song1", path="/music/a.mp3", cue_time=5)

    assert library.delete_track(lookalike) is False
    assert library.get_track("song1") is not None


def test_delete_track_removes_from_library(library, make_track):
    library.create_track(make_track(name="song1"))
    track = library.get_track("song1")

    assert library.delete_track(track) is True
    assert library.get_track("song1") is None


def test_delete_track_persists_to_database(library, make_track):
    library.create_track(make_track(name="song1"))
    reloaded = reload(library)
    track = reloaded.get_track("song1")

    reloaded.delete_track(track)

    assert reload(library).get_track("song1") is None


def test_delete_track_persists_and_preserves_other_tracks(library, make_track):
    library.create_track(make_track(name="song1"))
    library.create_track(make_track(name="song2"))
    library.create_track(make_track(name="song3"))

    library.delete_track(library.get_track("song2"))

    names = {t.name for t in reload(library).get_tracks()}
    assert names == {"song1", "song3"}


def test_full_crud_lifecycle_through_database(library, make_track):
    # Create
    library.create_track(make_track(name="song1", path="/music/a.mp3", cue_time=5))
    assert reload(library).get_track("song1").path == "/music/a.mp3"

    # Update
    track_id = reload(library).get_track("song1").id
    library.update_track(track_id, make_track(name="song1", path="/music/b.mp3", cue_time=15))
    assert reload(library).get_track("song1").path == "/music/b.mp3"

    # Delete
    persisted = reload(library)
    persisted.delete_track(persisted.get_track("song1"))
    assert reload(library).get_track("song1") is None
