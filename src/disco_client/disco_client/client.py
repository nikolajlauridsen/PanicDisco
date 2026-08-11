import requests

from disco_client.clients.TrackClient import TrackClient


class DiscoClient:
    """HTTP wrapper around disco_server's JSON API."""

    def __init__(self, base_url: str, timeout: float = 10.0):
        self.base_url = base_url.rstrip('/')
        self.timeout = timeout
        self.session = requests.Session()
        self.tracks = TrackClient(self.session, self.base_url, self.timeout)

