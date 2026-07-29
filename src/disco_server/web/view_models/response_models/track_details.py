from pydantic import BaseModel, ConfigDict, Field


class TrackDetails(BaseModel):
    model_config = ConfigDict(from_attributes=True, populate_by_name=True)

    id: int
    name: str
    cue_point: int | None = Field(validation_alias='cue_time')
    path: str