import os
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

print("Adding tracks to library...")
library = create_library(directory, files)
print("Done")