import os
from pathlib import Path

from requests import Session

from disco_shared.models.track_details import TrackDetails
from disco_shared.models.track_entity import TrackEntity
from disco_shared.models.track_update import TrackUpdate
from disco_shared.models.track_upload import TrackUpload

from disco_client.clients.client_base import ClientBase


class TrackClient(ClientBase):
    """HTTP client for disco_server's /api/tracks endpoints."""

    def __init__(self, session: Session | None, base_url: str, timeout: float | int) -> None:
        """base_url is disco_server's root URL (e.g. http://disco-server:5000)
        - /api/tracks gets appended once here, so callers/other methods never
        repeat it.
        """
        base_url = f"{base_url.rstrip('/')}/api/tracks"
        super().__init__(session, base_url, timeout)

    def list_tracks(self) -> list[TrackEntity]:
        """List every track (id + name only - see get_track for full details)."""
        response = self.session.get(self.base_url, timeout=self.timeout)
        self._raise_for_status(response)
        return [TrackEntity.model_validate(track) for track in response.json()]

    def get_track(self, track_id: int) -> TrackDetails:
        """Get full details for one track. Raises TrackNotFoundError if it doesn't exist."""
        response = self.session.get(f"{self.base_url}/{track_id}", timeout=self.timeout)
        self._raise_for_status(response)
        return TrackDetails.model_validate(response.json())

    def get_track_file(self, track_id: int) -> bytes:
        """Get the raw audio bytes for a track.

        Raises TrackNotFoundError if the track doesn't exist, or if its
        underlying file is missing on the server.
        """
        response = self.session.get(f"{self.base_url}/{track_id}/file", timeout=self.timeout)
        self._raise_for_status(response)
        return response.content

    def update_track(self, track_id: int, track: TrackUpdate) -> None:
        """Replace a track's name/cue_point/path. Raises TrackNotFoundError if
        it doesn't exist.

        TrackDetails.for_update() is usually the easiest way to build the
        TrackUpdate, since it starts from the track's current values.
        """
        response = self.session.put(f"{self.base_url}/{track_id}", json=track.model_dump(), timeout=self.timeout)
        self._raise_for_status(response)

    def delete_track(self, track_id: int) -> None:
        """Delete a track (and its underlying file, server-side). Raises
        TrackNotFoundError if it doesn't exist.
        """
        response = self.session.delete(f"{self.base_url}/{track_id}", timeout=self.timeout)
        self._raise_for_status(response)

    def upload_track(self, file_path: str | os.PathLike, track: TrackUpload) -> int:
        """Upload a track file and return the id of the created track.

        Raises DiscoAPIError if the file's extension isn't one of
        .mp3/.wav/.flac, or if the metadata in `track` fails server-side
        validation.
        """
        file_path = Path(file_path)
        with file_path.open('rb') as file:
            files = {'file': (file_path.name, file)}
            response = self.session.post(
                f"{self.base_url}/upload", files=files, data=track.model_dump(), timeout=self.timeout
            )
        self._raise_for_status(response)
        return int(response.headers['Location'].rstrip('/').rsplit('/', 1)[-1])

