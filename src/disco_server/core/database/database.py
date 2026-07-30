import os
from sqlalchemy import create_engine
from sqlalchemy.orm import scoped_session, sessionmaker
from disco_server.core.database.dtos.base import Base
from disco_server.core.database.dtos.track_dto import TrackDTO
from disco_server.core.database.mapping.mapper import map_to_dto, map_to_track
from disco_server.core.models.track import Track


class Database:
    def __init__(self, db_path: str):
        os.makedirs(os.path.dirname(db_path), exist_ok=True)
        self._engine = create_engine(f'sqlite:///{db_path}')
        self.db_sessions = scoped_session(sessionmaker(autocommit=False, autoflush=False, bind=self._engine))
        Base.query = self.db_sessions.query_property()

    def init_db(self):
        print('Initializing database...')
        Base.metadata.create_all(bind=self._engine)

    def _get_dto(self, track_id: int) -> TrackDTO | None:
        return TrackDTO.query.filter(TrackDTO.id == track_id).first()

    def add_track(self, track: Track) -> Track:
        dto = map_to_dto(track)
        self.db_sessions.add(dto)
        self.db_sessions.commit()
        track.id = dto.id
        return track

    def remove_track(self, track: Track) -> None:
        """Delete the track matching ``track.id``.

        Re-fetches the row by id via this session rather than deleting
        ``track`` directly, since ``track`` is a plain domain object with no
        ORM state to delete. No-op if the id no longer exists.
        """
        dto = self._get_dto(track.id)

        if dto is None:
            return

        self.db_sessions.delete(dto)
        self.db_sessions.commit()

    def update_track(self, track_id: int, track: Track) -> Track | None:
        """Update the persisted track matching ``track_id`` with ``track``'s data.

        Returns the updated track as read back from the database, or None if
        no track with that id exists.
        """
        dto = self._get_dto(track_id)

        if dto is None:
            return None

        dto.name = track.name
        dto.path = track.path
        dto.cue_time = track.cue_time
        self.db_sessions.commit()
        return map_to_track(dto)

    def get_tracks(self) -> list[Track]:
        return [map_to_track(dto) for dto in TrackDTO.query.all()]

    def get_track(self, track_id: int) -> Track | None:
        """Return the track with the given id, or None if not found."""
        dto = self._get_dto(track_id)
        return map_to_track(dto) if dto is not None else None
