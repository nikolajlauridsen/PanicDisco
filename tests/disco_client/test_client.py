from disco_client import DiscoClient
from disco_client.clients.boombox_client import BoomboxClient
from disco_client.clients.panic_client import PanicClient
from disco_client.clients.track_client import TrackClient


def test_endpoint_group_clients_share_one_session():
    client = DiscoClient("http://disco-server.test")

    assert isinstance(client.tracks, TrackClient)
    assert isinstance(client.boombox, BoomboxClient)
    assert isinstance(client.panic, PanicClient)
    assert client.tracks.session is client.session
    assert client.boombox.session is client.session
    assert client.panic.session is client.session


def test_base_url_strips_trailing_slash():
    client = DiscoClient("http://disco-server.test/")

    assert client.base_url == "http://disco-server.test"
    assert client.tracks.base_url == "http://disco-server.test/api/tracks"
    assert client.boombox.base_url == "http://disco-server.test/api/boombox"
    assert client.panic.base_url == "http://disco-server.test/api/panic"
