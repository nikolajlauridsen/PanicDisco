from pydantic import BaseModel, ConfigDict, Field

from disco_shared.models.track_update import TrackUpdate


class TrackDetails(BaseModel):
    model_config = ConfigDict(from_attributes=True, populate_by_name=True)

    id: int
    name: str
    cue_point: int | None = Field(validation_alias='cue_time')
    path: str

    def for_update(self) -> TrackUpdate:
        """Build a TrackUpdate pre-populated with this track's current fields,
        so callers only need to change what they actually want to update.
        """
        return TrackUpdate(name=self.name, cue_point=self.cue_point, path=self.path)