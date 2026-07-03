import vlc
from vlc import MediaPlayer

from disco_server.core.models.Track import Track

class Boombox:

    def __init__(self):
        self.loaded_track : Track = None
        self.player : MediaPlayer = None

    def _ensure_loaded(self):
        if self.player is None or self.loaded_track is None:
            raise RuntimeError("Boombox not loaded")

    def load_track(self, track: Track):
        self.loaded_track = track
        self.player = vlc.MediaPlayer(f"file://{track.path}")

    def play(self):
        self._ensure_loaded()
        self.player.play()
        # TODO: If this turns out to be too slow, move it to load_track, mute, play, set time and pause, then unmute
        if self.loaded_track.cue_time:
            # Set time is in ms
            self.player.set_time(self.loaded_track.cue_time * 1000)

    def stop(self):
        self._ensure_loaded()
        self.player.stop()

    def pause(self):
        self._ensure_loaded()
        self.player.set_pause(1)

