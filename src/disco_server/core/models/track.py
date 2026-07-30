from dataclasses import dataclass, field


@dataclass
class Track:
    """A track, keyed by id — names aren't unique, so equality only compares id."""

    name: str = field(compare=False)
    path: str = field(compare=False)
    cue_time: int | None = field(default=None, compare=False)
    id: int | None = None
