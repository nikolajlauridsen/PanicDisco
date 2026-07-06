from disco_server.core.models.track import Track
from disco_server.core.database.database import Database
from disco_server.core.database.dtos.track_dto import TrackDTO

class TrackLibrary:
    """Collection of Track objects, keyed by track name."""

    def __init__(self, database : Database) -> None:
        self.database : Database = database
        self._tracks: list[Track] = [self._map_from_dto(track) for track in self.database.get_tracks()]

    @staticmethod
    def _map_to_dto(track : Track) -> TrackDTO:
        return TrackDTO(name=track.name, path=track.path, cue_point=track.cue_time)

    @staticmethod
    def _map_from_dto(dto: TrackDTO) -> Track:
        return Track(name=dto.name, path=dto.path, cue_time=dto.cue_point)

    def create_track(self, track : Track) -> None:
        """Add a new track to the library."""
        self.database.add_track(self._map_to_dto(track))
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
