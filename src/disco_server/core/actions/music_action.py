from disco_server.core.extension.panic_action import PanicAction
from disco_server.services import get_boombox


class MusicAction(PanicAction):
    """Panic action that starts playback of whatever track is loaded."""

    def execute(self) -> None:
        boombox = get_boombox()
        boombox.play()
