from flask import current_app

from disco_server.core.extension.panic_action import PanicAction
from disco_server.core.services.boombox import Boombox
from disco_server.core.services.last_played import LastPlayed
from disco_server.core.services.panic import Panic
from disco_server.core.services.track_library import TrackLibrary

_TRACK_LIBRARY_KEY = 'track_library'
_BOOMBOX_KEY = 'boombox'
_PANIC_ACTION_KEY = 'panic_action'
_LAST_PLAYED_KEY = 'last_played'


def get_track_library() -> TrackLibrary:
    """Return the app's shared TrackLibrary, creating it on first access."""
    if _TRACK_LIBRARY_KEY not in current_app.extensions:
        current_app.extensions[_TRACK_LIBRARY_KEY] = TrackLibrary(current_app.database)
    return current_app.extensions[_TRACK_LIBRARY_KEY]


def get_boombox() -> Boombox:
    """Return the app's shared Boombox, creating it on first access."""
    if _BOOMBOX_KEY not in current_app.extensions:
        current_app.extensions[_BOOMBOX_KEY] = Boombox(current_app.config['VLC_ARGS'])
    return current_app.extensions[_BOOMBOX_KEY]

def add_panic_action(action: PanicAction) -> None:
    """Register `action` to run whenever the panic button is triggered."""
    if _PANIC_ACTION_KEY not in current_app.extensions:
        current_app.extensions[_PANIC_ACTION_KEY] = []

    current_app.extensions[_PANIC_ACTION_KEY].append(action)

def get_panic() -> Panic:
    """Return a Panic wrapping the app's currently registered panic actions."""
    if _PANIC_ACTION_KEY not in current_app.extensions:
        current_app.extensions[_PANIC_ACTION_KEY] = []

    return Panic(current_app.extensions[_PANIC_ACTION_KEY])

def get_last_played() -> LastPlayed:
    """Return a KeyValueService wrapping the app's currently registered key values."""
    if _LAST_PLAYED_KEY not in current_app.extensions:
        current_app.extensions[_LAST_PLAYED_KEY] = LastPlayed(current_app.database)

    return current_app.extensions[_LAST_PLAYED_KEY]