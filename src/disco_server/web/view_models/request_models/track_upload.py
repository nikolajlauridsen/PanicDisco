from pydantic import BaseModel, ConfigDict


class TrackUpload(BaseModel):
    model_config = ConfigDict(from_attributes=True, populate_by_name=True)

    name: str
    cue_point: int
