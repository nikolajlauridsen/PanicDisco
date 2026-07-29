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

import threading

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
    assert library.get_track(9999) is None


def test_create_track_is_readable_in_memory(library, make_track):
    track = make_track(name="song1")
    library.create_track(track)

    assert library.get_track(track.id) is track


def test_create_track_persists_to_database(library, make_track):
    track = make_track(name="song1", path="/music/song1.mp3", cue_time=42)
    library.create_track(track)

    reloaded = reload(library).get_track(track.id)

    assert reloaded is not None
    assert reloaded.name == "song1"
    assert reloaded.path == "/music/song1.mp3"
    assert reloaded.cue_time == 42


def test_create_track_assigns_database_id(library, make_track):
    track = make_track(name="song1", id=None)
    library.create_track(track)

    reloaded = reload(library).get_track(track.id)

    assert reloaded.id is not None


def test_create_assigns_in_memory_id(library, make_track):
    track = make_track(name="song1")
    library.create_track(track)
    assert library.get_track(track.id).id is not None


def test_create_multiple_tracks_persist(library, make_track):
    library.create_track(make_track(name="song1"))
    library.create_track(make_track(name="song2"))
    library.create_track(make_track(name="song3"))

    names = {t.name for t in reload(library).get_tracks()}

    assert names == {"song1", "song2", "song3"}


def test_create_track_with_no_cue_time_persists_as_null(library, make_track):
    track = make_track(name="song1", cue_time=None)
    library.create_track(track)

    reloaded = reload(library).get_track(track.id)

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
    track = make_track(name="song1", path="/music/song1.mp3", cue_time=7)
    library.create_track(track)

    reopened_library = TrackLibrary(Database(db_path=db_path))
    reloaded = reopened_library.get_track(track.id)

    assert reloaded is not None
    assert reloaded.path == "/music/song1.mp3"
    assert reloaded.cue_time == 7


def test_update_track_returns_false_when_missing(library, make_track):
    assert library.update_track(9999, make_track(name="nope")) is False


def test_update_track_returns_true_when_present(library, make_track):
    track = make_track(name="song1")
    library.create_track(track)

    assert library.update_track(track.id, make_track(name="song1", cue_time=99)) is True


def test_update_track_changes_in_memory_state(library, make_track):
    track = make_track(name="song1", cue_time=10)
    library.create_track(track)

    library.update_track(track.id, make_track(name="song1", cue_time=99, id=track.id))

    assert library.get_track(track.id).cue_time == 99


def test_update_track_persists_to_database(library, make_track):
    track = make_track(name="song1", cue_time=10)
    library.create_track(track)

    library.update_track(track.id, make_track(name="song1", path="/music/new.mp3", cue_time=99))

    reloaded = reload(library).get_track(track.id)

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
    track = make_track(name="song1", path="/music/a.mp3", cue_time=5)
    library.create_track(track)

    lookalike = make_track(name="song1", path="/music/a.mp3", cue_time=5)

    assert library.delete_track(lookalike) is False
    assert library.get_track(track.id) is not None


def test_delete_track_removes_from_library(library, make_track):
    track = make_track(name="song1")
    library.create_track(track)

    assert library.delete_track(track) is True
    assert library.get_track(track.id) is None


def test_delete_track_removes_track_from_in_memory_list(library, make_track):
    """get_tracks() reads straight from the in-memory list, so this checks
    delete_track actually removes the track from it rather than relying on
    get_track's own lookup over that same list.
    """
    track = make_track(name="song1")
    library.create_track(track)

    library.delete_track(track)

    assert track not in library.get_tracks()


def test_delete_track_persists_to_database(library, make_track):
    track = make_track(name="song1")
    library.create_track(track)
    reloaded = reload(library)
    fetched = reloaded.get_track(track.id)

    reloaded.delete_track(fetched)

    assert reload(library).get_track(track.id) is None


def test_delete_track_persists_and_preserves_other_tracks(library, make_track):
    library.create_track(make_track(name="song1"))
    track2 = make_track(name="song2")
    library.create_track(track2)
    library.create_track(make_track(name="song3"))

    library.delete_track(library.get_track(track2.id))

    names = {t.name for t in reload(library).get_tracks()}
    assert names == {"song1", "song3"}


def test_update_track_persists_when_called_from_a_different_thread(library, make_track, db_path):
    """Reproduces a real bug: Database's scoped_session is thread-scoped, but
    TrackLibrary caches Track objects for the app's entire lifetime. Under
    `flask run`'s default --with-threads dev server, a request can land on a
    different thread than the one that first built the library. Mutating the
    cached object and committing from that other thread's own (unrelated,
    empty) session is a silent no-op: update_track reports success, but
    nothing is actually written to the database.

    Note this must check persistence via a brand new Database (its own engine
    and scoped_session registry), not via reload()'s ``TrackLibrary(library.
    database)`` — reusing the same Database from the same (main) thread would
    just return the identity-mapped, still-dirty in-memory object from that
    thread's own session, which is a false positive: it looks persisted but
    was never actually flushed to disk. Only a genuinely separate Database,
    as used here (and in test_track_survives_a_fresh_database_instance_on_the
    _same_file), simulates an app restart closely enough to catch this.
    """
    track = make_track(name="song1", cue_time=10)
    library.create_track(track)
    track_id = track.id

    result = {}

    def do_update():
        result["ok"] = library.update_track(
            track_id, make_track(name="song1", path="/music/new.mp3", cue_time=99)
        )

    thread = threading.Thread(target=do_update)
    thread.start()
    thread.join()

    assert result["ok"] is True

    reloaded = TrackLibrary(Database(db_path=db_path)).get_track(track_id)
    assert reloaded.cue_time == 99
    assert reloaded.path == "/music/new.mp3"


def test_delete_track_persists_when_called_from_a_different_thread(library, make_track, db_path):
    """Same underlying issue as the update case, for delete_track. See the
    docstring on test_update_track_persists_when_called_from_a_different_thread
    for why this must check persistence via a brand new Database rather than
    reload()."""
    track = make_track(name="song1")
    library.create_track(track)
    track_id = track.id

    result = {}

    def do_delete():
        result["ok"] = library.delete_track(library.get_track(track_id))

    thread = threading.Thread(target=do_delete)
    thread.start()
    thread.join()

    assert result["ok"] is True
    assert TrackLibrary(Database(db_path=db_path)).get_track(track_id) is None


def test_full_crud_lifecycle_through_database(library, make_track):
    # Create
    track = make_track(name="song1", path="/music/a.mp3", cue_time=5)
    library.create_track(track)
    assert reload(library).get_track(track.id).path == "/music/a.mp3"

    # Update
    library.update_track(track.id, make_track(name="song1", path="/music/b.mp3", cue_time=15))
    assert reload(library).get_track(track.id).path == "/music/b.mp3"

    # Delete
    persisted = reload(library)
    persisted.delete_track(persisted.get_track(track.id))
    assert reload(library).get_track(track.id) is None
