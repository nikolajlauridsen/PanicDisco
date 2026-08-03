import os

from disco_server import create_app


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
