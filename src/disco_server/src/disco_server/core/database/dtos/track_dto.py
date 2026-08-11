from sqlalchemy.orm import Mapped
from sqlalchemy.orm import mapped_column

from disco_server.core.database.dtos.base import Base


class TrackDTO(Base):
    """The persisted database row for a track."""

    __tablename__ = 'track'

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column()
    path: Mapped[str] = mapped_column()
    cue_time: Mapped[int | None] = mapped_column()
