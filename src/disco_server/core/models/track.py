from dataclasses import dataclass


@dataclass
class Track:
    path: str
    name: str
    cue_time: int | None

