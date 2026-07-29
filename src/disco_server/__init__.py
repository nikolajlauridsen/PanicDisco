import os

from flask import Flask

from disco_server.core.database.database import Database

def create_app(test_config: dict | None = None):
    app = Flask(__name__, instance_relative_config=True)

    print(f"Instance path {app.instance_path}")
    os.makedirs(app.instance_path, exist_ok=True)

    app.config.from_mapping(
        DATABASE_PATH=os.path.join(app.instance_path, 'disco_server.sqlite3'),
    )
    if test_config is None:
        app.config.from_pyfile('config.py', silent=True)
    else:
        app.config.from_mapping(test_config)

    app.database = Database(db_path=app.config['DATABASE_PATH'])
    app.database.init_db()

    @app.route('/hello')
    def hello():
        return 'Hello, World!'

    return app

