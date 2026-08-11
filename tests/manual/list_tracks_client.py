from disco_client import DiscoClient

BASE_URL = "http://localhost:5000"

client = DiscoClient(BASE_URL)

print("="*5 + "Tracks" + "="*5)
for track in client.tracks.list_tracks():
    print(f"{track.id}: {track.name}")
