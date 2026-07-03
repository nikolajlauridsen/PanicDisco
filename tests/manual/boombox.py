import time

from disco_server.core.services.boombox import Boombox
from disco_server.core.models.track import Track

track = Track(name="Pirouette", cue_time=50, path="/home/mole/Music/Made in Heights/ENEMY [2015]/02 Pirouette.mp3")
print(f"Loading track {track.name} at {track.path}")
boombox = Boombox()
try:
    boombox.load_track(track)
    boombox.play()
    print("Playing track")
    while True:
        time.sleep(0.5)
except KeyboardInterrupt:
    pass
finally:
    print("Stopping track")
    boombox.stop()