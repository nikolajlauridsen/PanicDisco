import os
from sqlalchemy import create_engine
from sqlalchemy.orm import scoped_session, sessionmaker
from disco_server.core.database.dtos.base import Base
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

    def add_track(self, track: Track) -> Track:
        self.db_sessions.add(track)
        self.db_sessions.commit()
        return track

    def remove_track(self, track: Track) -> None:
        """Delete the track matching ``track.id``.

        Re-fetches by id via this session rather than deleting ``track``
        directly, since a track instance loaded by another session/thread
        isn't attached to this one and would raise on delete. No-op if the
        id no longer exists.
        """
        found_track = self.get_track(track.id)

        if found_track is None:
            return

        self.db_sessions.delete(found_track)
        self.db_sessions.commit()

    def save_changes(self) -> None:
        self.db_sessions.commit()

    def get_tracks(self) -> list[Track]:
        return Track.query.all()

    def get_track(self, track_id: int) -> Track | None:
        """Return the track with the given id, or None if not found."""
        return Track.query.filter(Track.id == track_id).first()
