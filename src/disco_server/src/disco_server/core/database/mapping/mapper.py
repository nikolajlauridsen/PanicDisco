from disco_server.core.database.dtos.track_dto import TrackDTO
from disco_core.models.track import Track


def map_to_track(dto: TrackDTO) -> Track:
    return Track(
        id=dto.id,
        name=dto.name,
        path=dto.path,
        cue_time=dto.cue_time,
    )


def map_to_dto(track: Track) -> TrackDTO:
    return TrackDTO(
        id=track.id,
        name=track.name,
        path=track.path,
        cue_time=track.cue_time,
    )
