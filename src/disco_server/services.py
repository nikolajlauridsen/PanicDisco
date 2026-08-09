from flask import current_app

from disco_server.core.extension.panic_action import PanicAction
from disco_server.core.services.boombox import Boombox
from disco_server.core.services.panic import Panic
from disco_server.core.services.track_library import TrackLibrary


def get_track_library() -> TrackLibrary:
    """Return the app's shared TrackLibrary, creating it on first access."""
    if 'track_library' not in current_app.extensions:
        current_app.extensions['track_library'] = TrackLibrary(current_app.database)
    return current_app.extensions['track_library']


def get_boombox() -> Boombox:
    """Return the app's shared Boombox, creating it on first access."""
    if 'boombox' not in current_app.extensions:
        current_app.extensions['boombox'] = Boombox(current_app.config['VLC_ARGS'])
    return current_app.extensions['boombox']

def add_panic_action(action: PanicAction) -> None:
    """Register `action` to run whenever the panic button is triggered."""
    if 'panic_action' not in current_app.extensions:
        current_app.extensions['panic_action'] = []

    current_app.extensions['panic_action'].append(action)

def get_panic() -> Panic:
    """Return a Panic wrapping the app's currently registered panic actions."""
    if 'panic_action' not in current_app.extensions:
        current_app.extensions['panic_action'] = []

    return Panic(current_app.extensions['panic_action'])