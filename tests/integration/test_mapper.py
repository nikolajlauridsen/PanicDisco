from disco_server.web.mapping import mapper
from disco_shared.models.track_details import TrackDetails


def test_map_to_track_details_maps_matching_fields(make_track):
    track = make_track(name="song1", path="/music/song1.mp3", cue_time=5, id=1)

    details = mapper.map_to_track_details(track)

    assert isinstance(details, TrackDetails)
    assert details.id == 1
    assert details.name == "song1"
    assert details.path == "/music/song1.mp3"


def test_map_to_track_details_renames_cue_time_to_cue_point(make_track):
    track = make_track(cue_time=42, id=1)

    details = mapper.map_to_track_details(track)

    assert details.cue_point == 42


def test_map_to_track_details_allows_missing_cue_time(make_track):
    track = make_track(cue_time=None, id=1)

    details = mapper.map_to_track_details(track)

    assert details.cue_point is None
