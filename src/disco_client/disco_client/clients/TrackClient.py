from requests import Session

from disco_shared.models.track_details import TrackDetails
from disco_shared.models.track_entity import TrackEntity

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
        
