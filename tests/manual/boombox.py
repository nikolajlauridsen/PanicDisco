import time

from disco_server import create_app
from disco_server.core.services.boombox import Boombox
from disco_server.core.services.track_library import TrackLibrary
from disco_core.models.track import Track

app = create_app()
library = TrackLibrary(app.database)

print("="*5 + "Tracks" + "="*5)
tracks = library.get_tracks()
for (track, index) in zip(tracks, range(len(tracks))):
    print(f"{index + 1}: {track.name} at {track.cue_time} seconds")

choice = int(input("Choose track: "))
chosen_track = tracks[choice-1]

boombox = Boombox()
try:
    print("Loading")
    boombox.load_track(chosen_track)
    print(f"Playing loaded track {boombox.loaded_track.name} at {boombox.loaded_track.cue_time}")
    boombox.play()
    while True:
        time.sleep(0.5)
except KeyboardInterrupt:
    pass
finally:
    print("Stopping track")
    boombox.stop()

