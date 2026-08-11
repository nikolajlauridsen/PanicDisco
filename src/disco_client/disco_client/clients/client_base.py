import requests
from requests import Session

from disco_client.errors import TrackNotFoundError, BoomboxNotLoadedError, DiscoAPIError


class ClientBase:

    def __init__(self, session : Session | None, base_url: str, timeout: float | int = 10.0):
        self.base_url = base_url
        self.timeout = timeout
        self.session = session if session else requests.Session()

    def _raise_for_status(self, response: requests.Response) -> None:
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
