"""Interactive proof-of-concept CLI for disco_client - list/get/upload/
update/delete tracks against a real running disco_server, driven entirely
through the client library (no direct HTTP calls of its own).

Run via disco_client's venv (needs a disco_server instance already running):
    src/disco_client/.venv/bin/python tests/manual/track_manager.py
"""
import requests

from disco_client import DiscoAPIError, DiscoClient, TrackNotFoundError
from disco_shared.models.track_upload import TrackUpload

BASE_URL = "http://localhost:5000"

client = DiscoClient(BASE_URL)

MENU = """
==== PanicDisco Track Manager ====
1. List tracks
2. Get track details
3. Upload a track
4. Update a track
5. Delete a track
6. Quit
"""


def list_tracks():
    tracks = client.tracks.list_tracks()
    if not tracks:
        print("No tracks yet.")
        return
    for track in tracks:
        print(f"{track.id}: {track.name}")


def get_track():
    track_id = int(input("Track id: "))
    details = client.tracks.get_track(track_id)
    print(f"name={details.name!r} cue_point={details.cue_point} path={details.path!r}")


def upload_track():
    file_path = input("Path to audio file (.mp3/.wav/.flac): ").strip()
    name = input("Name: ").strip()
    cue_point = int(input("Cue point (seconds): "))

    track_id = client.tracks.upload_track(file_path, TrackUpload(name=name, cue_point=cue_point))
    print(f"Uploaded as track {track_id}")


def update_track():
    track_id = int(input("Track id: "))
    details = client.tracks.get_track(track_id)
    print(f"Current: name={details.name!r} cue_point={details.cue_point}")

    update = details.for_update()

    new_name = input(f"New name [{details.name}]: ").strip()
    if new_name:
        update.name = new_name

    new_cue_point = input(f"New cue point, or 'none' to clear [{details.cue_point}]: ").strip()
    if new_cue_point.lower() == "none":
        update.cue_point = None
    elif new_cue_point:
        update.cue_point = int(new_cue_point)

    client.tracks.update_track(track_id, update)
    print("Updated")


def delete_track():
    track_id = int(input("Track id: "))
    if input(f"Delete track {track_id}? [y/N] ").strip().lower() != "y":
        print("Cancelled")
        return

    client.tracks.delete_track(track_id)
    print("Deleted")


ACTIONS = {
    "1": list_tracks,
    "2": get_track,
    "3": upload_track,
    "4": update_track,
    "5": delete_track,
}

while True:
    print(MENU)
    choice = input("Choice: ").strip()

    if choice == "6":
        break

    action = ACTIONS.get(choice)
    if action is None:
        print("Not a valid choice")
        continue

    try:
        action()
    except TrackNotFoundError:
        print("No track with that id")
    except DiscoAPIError as e:
        print(f"Server error: {e.message}")
    except requests.exceptions.ConnectionError:
        print(f"Couldn't reach disco_server at {BASE_URL} - is it running?")
    except (ValueError, FileNotFoundError) as e:
        print(f"Invalid input: {e}")
