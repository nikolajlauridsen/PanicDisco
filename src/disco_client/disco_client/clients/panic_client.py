from requests import Session

from disco_client.clients.client_base import ClientBase


class PanicClient(ClientBase):
    """HTTP client for disco_server's /api/panic endpoints."""

    def __init__(self, session: Session, base_url: str, timeout: float | int) -> None:
        """base_url is disco_server's root URL (e.g. http://disco-server:5000)
        - /api/panic gets appended once here, so callers/other methods never
        repeat it.
        """
        base_url = f"{base_url.rstrip('/')}/api/panic"
        super().__init__(session, base_url, timeout)

    def start(self) -> None:
        """Activate panic mode: runs every registered PanicAction's start()
        server-side. Has no documented failure mode - the server swallows
        each action's exceptions individually, so this always succeeds.
        """
        response = self.session.post(f"{self.base_url}/start", timeout=self.timeout)
        self._raise_for_status(response)

    def stop(self) -> None:
        """Stop panic mode: runs every registered PanicAction's stop()
        server-side. Has no documented failure mode - the server swallows
        each action's exceptions individually, so this always succeeds.
        """
        response = self.session.post(f"{self.base_url}/stop", timeout=self.timeout)
        self._raise_for_status(response)
