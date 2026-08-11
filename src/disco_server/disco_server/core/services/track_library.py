from disco_core.models.track import Track
from disco_server.core.database.database import Database

class TrackLibrary:
    """Collection of Track objects, keyed by id (names aren't unique)."""

    def __init__(self, database : Database) -> None:
        self.database : Database = database
        self._tracks: list[Track] = list(self.database.get_tracks())

    def create_track(self, track : Track) -> None:
        """Add a new track to the library."""
        self.database.add_track(track)
        self._tracks.append(track)

    def delete_track(self, track : Track) -> bool:
        """Remove a track from the library.

        ``track`` must share its id with an entry in the in-memory list
        (``Track`` equality only compares id, not other fields) for the
        delete to proceed; the database delete itself re-fetches by id so it
        works regardless of which session/thread loaded ``track``.

        Returns true if track was removed.
        """

        if track not in self._tracks:
            return False

        self.database.remove_track(track)
        self._tracks.remove(track)
        return True

    def get_track(self, track_id : int) -> Track | None:
        """Return the track with the given id, or None if not found."""
        for track in self._tracks:
            if track.id == track_id:
                return track
        return None

    def get_tracks(self) -> list[Track]:
        """Return a list of all tracks in the library."""
        return [track for track in self._tracks]

    def update_track(self, track_id : int, track : Track) -> bool:
        """Replace the track matching track_id with the given track's data.

        Names aren't unique, so matching by id avoids ambiguity when
        duplicate-named tracks exist. The update is delegated to the
        database (rather than mutating whatever object is in the in-memory
        list), so this works regardless of which session/thread loaded the
        in-memory copy; the in-memory list is then updated to hold the
        object the database returns, so any other reference to the old
        in-memory object won't see the change. ``Track`` equality only
        compares id, so ``list.index`` finds the stale entry even though its
        other fields differ from ``updated_track``.

        returns true if track was updated.
        """
        updated_track = self.database.update_track(track_id, track)
        if updated_track is None:
            return False

        try:
            found_index = self._tracks.index(updated_track)
        except ValueError:
            found_index = None

        if found_index is not None:
            self._tracks[found_index] = updated_track
        return True
