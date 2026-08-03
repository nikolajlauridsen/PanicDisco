from pydantic import ConfigDict, BaseModel


class TrackEntity(BaseModel):
    model_config = ConfigDict(from_attributes=True, populate_by_name=True)

    id: int
    name: str