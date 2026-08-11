from disco_server.core.models.track import Track
from disco_shared.models.track_update import TrackUpdate
from disco_shared.models.track_upload import TrackUpload
from disco_shared.models.track_details import TrackDetails
from disco_shared.models.track_entity import TrackEntity


def map_to_track_details(track: Track) -> TrackDetails:
    return TrackDetails.model_validate(track)

def map_to_track_entity(track: Track) -> TrackEntity:
    return TrackEntity.model_validate(track)

def map_to_track(track_update: TrackUpdate) -> Track:
    return Track(
        name=track_update.name,
        path=track_update.path,
        cue_time=track_update.cue_point,
    )

def map_upload_to_track(track_upload: TrackUpload, path : str) -> Track:
    return Track(
        name=track_upload.name,
        path=path,
        cue_time=track_upload.cue_point)