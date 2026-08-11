import os

from disco_server import create_app
from disco_server.core.services.track_library import TrackLibrary
from disco_core.models.track import Track

def create_library(database, directory : str, files: list[str]) -> TrackLibrary:
    library = TrackLibrary(database)

    print("Adding tracks to library...")
    for file in files:
        path = os.path.join(directory, file)
        track = Track(name=file, path=path, cue_time=50)
        library.create_track(track)

    return library

app = create_app()
app.database.init_db()

directory = input("Chose directory to play from: ")
files = [file for file in os.listdir(directory) if file.endswith(".mp3")]

library = create_library(app.database, directory, files)
print("Done")