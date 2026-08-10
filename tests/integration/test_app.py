import os

from disco_server import create_app, services


class FakeBoombox:
    """A fake Boombox that just records what got loaded, instead of touching real VLC."""

    def __init__(self, vlc_args=''):
        self.loaded_track = None

    def load_track(self, track):
        self.loaded_track = track


def test_create_app_wires_database_from_config(tmp_path):
    db_path = str(tmp_path / "test.db")

    app = create_app({"DATABASE_PATH": db_path})

    assert app.config["DATABASE_PATH"] == db_path
    assert app.database is not None


def test_create_app_wires_upload_folder_from_config(tmp_path):
    upload_folder = str(tmp_path / "uploads")

    app = create_app({"UPLOAD_FOLDER": upload_folder})

    assert app.config["UPLOAD_FOLDER"] == upload_folder
    assert os.path.isdir(upload_folder)


def test_init_db_command_creates_the_database_file(tmp_path):
    db_path = str(tmp_path / "test.db")
    app = create_app({"DATABASE_PATH": db_path})

    result = app.test_cli_runner().invoke(args=["init-db"])

    assert result.exit_code == 0
    assert os.path.exists(db_path)


def test_create_app_does_not_load_anything_when_no_track_was_ever_played(tmp_path, monkeypatch):
    """Regression test: create_app() must not crash for a database that's
    been initialized but has no recorded last-played track — Database.
    is_initialized() being true doesn't mean LastPlayed has anything to
    restore.
    """
    monkeypatch.setattr(services, "Boombox", FakeBoombox)

    db_path = str(tmp_path / "test.db")
    app = create_app({"DATABASE_PATH": db_path, "VLC_ARGS": ""})
    app.database.init_db()

    with app.app_context():
        boombox = services.get_boombox()

    assert boombox.loaded_track is None


def test_create_app_restores_the_last_played_track_into_boombox(tmp_path, monkeypatch, make_track):
    """create_app's startup step should reload whatever track was loaded
    before the previous shutdown, so restarting the server picks the
    boombox back up where it left off.
    """
    monkeypatch.setattr(services, "Boombox", FakeBoombox)

    db_path = str(tmp_path / "test.db")
    app = create_app({"DATABASE_PATH": db_path, "VLC_ARGS": ""})
    app.database.init_db()
    track = app.database.add_track(make_track(name="song1"))
    with app.app_context():
        services.get_last_played().set(track)

    restarted = create_app({"DATABASE_PATH": db_path, "VLC_ARGS": ""})
    with restarted.app_context():
        boombox = services.get_boombox()

    assert boombox.loaded_track is not None
    assert boombox.loaded_track.id == track.id
