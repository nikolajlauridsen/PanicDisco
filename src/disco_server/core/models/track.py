from sqlalchemy.orm import Mapped
from sqlalchemy.orm import mapped_column

from disco_server.core.database.dtos.base import Base


class Track(Base):
    """A track, both the domain model and the persisted database row."""

    __tablename__ = 'track'

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column()
    path: Mapped[str] = mapped_column()
    cue_time: Mapped[int | None] = mapped_column()

    def __repr__(self) -> str:
        return f'Track: {self.name}'
