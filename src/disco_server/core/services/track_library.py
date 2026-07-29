from disco_server.core.models.track import Track
from disco_server.core.database.database import Database

class TrackLibrary:
    """Collection of Track objects, keyed by track name."""

    def __init__(self, database : Database) -> None:
        self.database : Database = database
        self._tracks: list[Track] = list(self.database.get_tracks())

    def create_track(self, track : Track) -> None:
        """Add a new track to the library."""
        self.database.add_track(track)
        self._tracks.append(track)

    def delete_track(self, track : Track) -> bool:
        """Remove a track from the library.

        Returns true if track was removed.
        """

        if track not in self._tracks:
            return False

        self.database.remove_track(track)
        self._tracks.remove(track)
        return True

    def get_track(self, track_name : str) -> Track | None:
        """Return the track with the given name, or None if not found."""
        for track in self._tracks:
            if track.name == track_name:
                return track
        return None

    def get_tracks(self) -> list[Track]:
        """Return a list of all tracks in the library."""
        return [track for track in self._tracks]

    def update_track(self, track_id : int, track : Track) -> bool:
        """Replace the track matching track_id with the given track's data.

        Names aren't unique, so matching by id avoids ambiguity when
        duplicate-named tracks exist.

        returns true if track was updated.
        """
        for existing_track in self._tracks:
            if existing_track.id == track_id:
                existing_track.name = track.name
                existing_track.path = track.path
                existing_track.cue_time = track.cue_time
                self.database.save_changes()
                return True

        return False
