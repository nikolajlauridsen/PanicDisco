import requests
from requests import Session

from disco_client.errors import TrackNotFoundError, BoomboxNotLoadedError, DiscoAPIError


class ClientBase:
    """Shared base for endpoint-group clients (TrackClient, etc.).

    Holds the requests.Session, base_url, and timeout common to all of them,
    plus the error-mapping logic every one of them needs after a request.
    """

    def __init__(self, session: Session | None, base_url: str, timeout: float = 10.0):
        """session=None creates a private Session; pass one explicitly (as
        DiscoClient does) so multiple endpoint-group clients share one.
        """
        self.base_url = base_url
        self.timeout = timeout
        self.session = session if session is not None else requests.Session()

    def _raise_for_status(self, response: requests.Response) -> None:
        """Raise the disco_client exception matching the server's error
        response, reading the message off the shared Error model's JSON
        shape ({"error": ..., "status_code": ...}); does nothing for a 2xx
        response.

        404 -> TrackNotFoundError, 503 -> BoomboxNotLoadedError, anything
        else non-2xx -> the generic DiscoAPIError.
        """
        if response.ok:
            return

        try:
            message = response.json().get('error', response.reason)
        except ValueError:
            message = response.reason

        if response.status_code == 404:
            raise TrackNotFoundError(response.status_code, message)
        if response.status_code == 503:
            raise BoomboxNotLoadedError(response.status_code, message)
        raise DiscoAPIError(response.status_code, message)
