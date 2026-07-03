from disco_server.core.database.dtos.base import Base
from sqlalchemy.orm import Mapped
from sqlalchemy.orm import mapped_column

class TrackDTO(Base):

    __tablename__ = 'track'
    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column()
    path: Mapped[str] = mapped_column()
    cue_point: Mapped[int] = mapped_column()

    def __init__(self, name: str, path: str, cue_point: int) -> None:
        self.name = name
        self.path = path
        self.cue_point = cue_point

    def __repr__(self) -> str:
        return f'Track: {self.name}'
