import requests

from disco_client.clients.boombox_client import BoomboxClient
from disco_client.clients.track_client import TrackClient


class DiscoClient:
    """HTTP wrapper around disco_server's JSON API."""

    def __init__(self, base_url: str, timeout: float | int = 10.0):
        """base_url is disco_server's root URL, e.g. http://disco-server:5000.

        Endpoint-group clients hang off attributes here (`.tracks`,
        `.boombox`; a panic client would follow the same pattern) and all
        share this one Session/timeout.
        """
        self.base_url = base_url.rstrip('/')
        self.timeout = timeout
        self.session = requests.Session()
        self.tracks = TrackClient(self.session, self.base_url, self.timeout)
        self.boombox = BoomboxClient(self.session, self.base_url, self.timeout)

