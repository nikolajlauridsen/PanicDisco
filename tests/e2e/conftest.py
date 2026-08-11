import threading

import pytest
from werkzeug.serving import make_server

from disco_client import DiscoClient
from disco_server import create_app


@pytest.fixture
def live_server_url(tmp_path):
    """Runs a real disco_server instance on a real socket, in a background
    thread, for the duration of a test - so disco_client can be exercised
    against it over actual HTTP rather than Flask's fake test client. That's
    the whole point of this suite: prove the two sides actually agree on the
    wire format, which a mocked test can't do.
    """
    app = create_app({
        "DATABASE_PATH": str(tmp_path / "test.db"),
        "UPLOAD_FOLDER": str(tmp_path / "uploads"),
    })
    app.database.init_db()

    server = make_server("127.0.0.1", 0, app)
    thread = threading.Thread(target=server.serve_forever, daemon=True)
    thread.start()

    try:
        yield f"http://127.0.0.1:{server.server_port}"
    finally:
        server.shutdown()
        thread.join()


@pytest.fixture
def client(live_server_url):
    """A DiscoClient pointed at the live test server."""
    return DiscoClient(live_server_url)
