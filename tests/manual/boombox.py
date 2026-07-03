import time
import os

from disco_server.core.services.boombox import Boombox
from disco_server.core.services.track_library import TrackLibrary
from disco_server.core.models.track import Track


def create_library(directory : str, files: list[str]) -> TrackLibrary:
    library = TrackLibrary()

    print("Adding tracks to library...")
    for file in files:
        path = os.path.join(directory, file)
        track = Track(name=file, path=path, cue_time=50)
        library.create_track(track)

    return library

directory = input("Chose directory to play from: ")
files = [file for file in os.listdir(directory) if file.endswith(".mp3")]

library = create_library(directory, files)

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

