from requests import Session

from disco_client.clients.client_base import ClientBase


class BoomboxClient(ClientBase):
    """HTTP client for disco_server's /api/boombox endpoints."""

    def __init__(self, session: Session | None, base_url: str, timeout: float | int) -> None:
        """base_url is disco_server's root URL (e.g. http://disco-server:5000)
        - /api/boombox gets appended once here, so callers/other methods never
        repeat it.
        """
        base_url = f"{base_url.rstrip('/')}/api/boombox"
        super().__init__(session, base_url, timeout)

    def _control(self, action: str) -> None:
        """Shared PUT-and-raise logic behind play/stop/pause/resume, which
        differ only in which sub-path they hit.
        """
        response = self.session.put(f"{self.base_url}/{action}", timeout=self.timeout)
        self._raise_for_status(response)

    def load(self, track_id: int) -> None:
        """Load a track onto the boombox, replacing whatever was loaded
        before. Raises TrackNotFoundError if the track doesn't exist.
        """
        response = self.session.put(f"{self.base_url}/load/{track_id}", timeout=self.timeout)
        self._raise_for_status(response)

    def play(self) -> None:
        """Start playback of the loaded track. Raises BoomboxNotLoadedError
        if no track is loaded.
        """
        self._control('play')

    def stop(self) -> None:
        """Stop playback of the loaded track. Raises BoomboxNotLoadedError
        if no track is loaded.
        """
        self._control('stop')

    def pause(self) -> None:
        """Pause playback of the loaded track. Raises BoomboxNotLoadedError
        if no track is loaded.
        """
        self._control('pause')

    def resume(self) -> None:
        """Resume playback of the loaded track. Raises BoomboxNotLoadedError
        if no track is loaded.
        """
        self._control('resume')
