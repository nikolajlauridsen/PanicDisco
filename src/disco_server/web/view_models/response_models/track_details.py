from dataclasses import dataclass


@dataclass
class TrackDetails:
    id: int
    name: str
    cue_point: int
    path: str