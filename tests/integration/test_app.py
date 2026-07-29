import os

from disco_server import create_app


def test_create_app_wires_database_from_config(tmp_path):
    db_path = str(tmp_path / "test.db")

    app = create_app({"DATABASE_PATH": db_path})

    assert app.config["DATABASE_PATH"] == db_path
    assert os.path.exists(db_path)
