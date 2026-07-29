import os
from sqlalchemy import create_engine
from sqlalchemy.orm import scoped_session, sessionmaker
from disco_server.core.database.dtos.base import Base
from disco_server.core.models.track import Track


class Database:
    # TODO: Make the path come from configuration
    def __init__(self, db_path: str = r'C:\Users\nikol\Documents\Github\PanicDisco\tests\manual\tmp\test.db'):
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
        self.db_sessions.delete(track)
        self.db_sessions.commit()

    def save_changes(self) -> None:
        self.db_sessions.commit()

    def get_tracks(self) -> list[Track]:
        return Track.query.all()