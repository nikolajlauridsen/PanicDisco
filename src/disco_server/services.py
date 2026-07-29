from flask import current_app

from disco_server.core.services.boombox import Boombox
from disco_server.core.services.track_library import TrackLibrary


def get_track_library() -> TrackLibrary:
    """Return the app's shared TrackLibrary, creating it on first access."""
    if 'track_library' not in current_app.extensions:
        current_app.extensions['track_library'] = TrackLibrary(current_app.database)
    return current_app.extensions['track_library']


def get_boombox() -> Boombox:
    """Return the app's shared Boombox, creating it on first access."""
    if 'boombox' not in current_app.extensions:
        current_app.extensions['boombox'] = Boombox()
    return current_app.extensions['boombox']