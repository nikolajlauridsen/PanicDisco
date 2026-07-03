from sqlalchemy import create_engine
from sqlalchemy.orm import scoped_session, sessionmaker
from disco_server.core.database.dtos.base import Base
from disco_server.core.database.dtos.track_dto import TrackDTO


class Database:
    def __init__(self):
        # TODO: Move this
        self._engine = create_engine('sqlite:////tmp/test.db')
        self.db_sessions = scoped_session(sessionmaker(autocommit=False, autoflush=False, bind=self._engine))
        Base.query = self.db_sessions.query_property()

    def init_db(self):
        print('Initializing database...')
        Base.metadata.create_all(bind=self._engine)

    def add_track(self, track: TrackDTO) -> None:
        self.db_sessions.add(track)
        self.db_sessions.commit()

    def get_tracks(self) -> list[TrackDTO]:
        return TrackDTO.query.all()