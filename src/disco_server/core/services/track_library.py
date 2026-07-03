from disco_server.core.models.track import Track

class TrackLibrary:
    """Collection of Track objects, keyed by track name."""

    def __init__(self):
        self._tracks : list[Track] = []

    def create_track(self, track : Track) -> None:
        """Add a new track to the library."""
        self._tracks.append(track)

    def delete_track(self, track : Track) -> bool:
        """Remove a track from the library.

        Returns true if track was removed.
        """

        if track not in self._tracks:
            return False

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

    def update_track(self, track_name : str, track : Track) -> bool:
        """Replace the track matching track_name with the given track.

        returns true if track was updated.
        """
        updated = False
        for existing_track, index in zip(self._tracks, range(len(self._tracks))):
            if existing_track.name == track_name:
                self._tracks[index] = track
                updated = True

        return updated
