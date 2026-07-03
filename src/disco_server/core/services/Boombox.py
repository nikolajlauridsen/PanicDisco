import vlc
from vlc import MediaPlayer

from disco_server.core.models.Track import Track

class Boombox:
    """A single-track audio player backed by VLC.

    Wraps a `vlc.MediaPlayer` for one `Track` at a time, exposing simple
    load/play/pause/stop controls. A track must be loaded via `load_track`
    before any playback method is called.
    """

    def __init__(self):
        self.loaded_track : Track = None
        self._vlc_instance = vlc.Instance()
        self.player : MediaPlayer = self._vlc_instance.media_player_new()

    def _ensure_loaded(self):
        """Raise if no track has been loaded yet."""
        if self.loaded_track is None:
            raise RuntimeError("Boombox not loaded")

    def load_track(self, track: Track):
        """Load `track`.

        Does not start playback; call `play` afterwards.
        """
        self.loaded_track = track
        self.player = vlc.MediaPlayer(f"file://{track.path}")

    def play(self):
        """Start playback of the loaded track.

        If the track has a `cue_time`, seeks to it (in seconds) after
        starting playback.
        """
        self._ensure_loaded()
        self.player.play()
        # TODO: If this turns out to be too slow, move it to load_track, mute, play, set time and pause, then unmute
        if self.loaded_track.cue_time:
            # Set time is in ms
            self.player.set_time(self.loaded_track.cue_time * 1000)

    def stop(self):
        """Stop playback of the loaded track."""
        self._ensure_loaded()
        self.player.stop()

    def pause(self):
        """Pause playback of the loaded track."""
        self._ensure_loaded()
        self.player.set_pause(1)

