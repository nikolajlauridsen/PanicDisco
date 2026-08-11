import os
from pathlib import Path

from requests import Session

from disco_shared.models.track_details import TrackDetails
from disco_shared.models.track_entity import TrackEntity
from disco_shared.models.track_update import TrackUpdate
from disco_shared.models.track_upload import TrackUpload

from disco_client.clients.client_base import ClientBase


class TrackClient(ClientBase):

    def __init__(self, session: Session | None, base_url: str, timeout: float | int) -> None:
        base_url = f"{base_url.rstrip('/')}/api/tracks"
        super().__init__(session, base_url, timeout)

    def list_tracks(self) -> list[TrackEntity]:
        response = self.session.get(self.base_url, timeout=self.timeout)
        self._raise_for_status(response)
        return [TrackEntity.model_validate(track) for track in response.json()]

    def get_track(self, track_id: int) -> TrackDetails:
        response = self.session.get(f"{self.base_url}/{track_id}", timeout=self.timeout)
        self._raise_for_status(response)
        return TrackDetails.model_validate(response.json())

    def update_track(self, track_id: int, track: TrackUpdate) -> None:
        response = self.session.put(f"{self.base_url}/{track_id}", json=track.model_dump(), timeout=self.timeout)
        self._raise_for_status(response)

    def delete_track(self, track_id: int) -> None:
        response = self.session.delete(f"{self.base_url}/{track_id}", timeout=self.timeout)
        self._raise_for_status(response)

    def upload_track(self, file_path: str | os.PathLike, track: TrackUpload) -> int:
        """Upload a track file and return the id of the created track."""
        file_path = Path(file_path)
        with file_path.open('rb') as file:
            files = {'file': (file_path.name, file)}
            response = self.session.post(
                f"{self.base_url}/upload", files=files, data=track.model_dump(), timeout=self.timeout
            )
        self._raise_for_status(response)
        return int(response.headers['Location'].rstrip('/').rsplit('/', 1)[-1])

