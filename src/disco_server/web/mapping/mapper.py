from disco_server.core.models.track import Track
from disco_server.web.view_models.response_models.track_details import TrackDetails


def map_to_track_details(track: Track) -> TrackDetails:
    return TrackDetails.model_validate(track)