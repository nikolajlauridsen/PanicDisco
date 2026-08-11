from disco_server.core.database.database import Database
from disco_core.models.track import Track

_KEY = "last_played"

class LastPlayed:
    """Persists which track was last loaded, so it can be reloaded on startup.

    Reads/writes the track id directly through `Database` rather than
    `services.get_track_library()` — this keeps `LastPlayed` independent of
    `disco_server.services`/`current_app` (it's also what `services.py` and
    `core.services.last_played` importing each other would otherwise be, a
    circular import), and it's constructed with the same `Database` it uses
    to look the track back up, so there's no risk of resolving against a
    different app's data.
    """

    def __init__(self, database: Database) -> None:
        self.database = database

    def set(self, track: Track) -> None:
        if track.id is None:
            raise RuntimeError('Track id is required')

        self.database.set_value(_KEY, str(track.id))

    def get(self) -> Track | None:
        track_id = self.database.get_value(_KEY)
        if track_id is None:
            return None

        return self.database.get_track(int(track_id))