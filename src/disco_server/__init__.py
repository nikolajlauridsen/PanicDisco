import os

import click
from flasgger import Swagger
from flask import Flask

from disco_server.blueprints.tracks import bp as tracks_bp
from disco_server.blueprints.web import bp as web_bp
from disco_server.core.database.database import Database
from disco_server.web.json_provider import PydanticJSONProvider
from disco_server.web.swagger_template import build_swagger_template

def create_app(test_config: dict | None = None):
    app = Flask(__name__, instance_relative_config=True)
    app.json = PydanticJSONProvider(app)

    print(f"Instance path {app.instance_path}")
    os.makedirs(app.instance_path, exist_ok=True)

    app.config.from_mapping(
        DATABASE_PATH=os.path.join(app.instance_path, 'disco_server.sqlite3'),
        UPLOAD_FOLDER=os.path.join(app.instance_path, 'uploads'),
    )
    if test_config is None:
        app.config.from_pyfile('config.py', silent=True)
    else:
        app.config.from_mapping(test_config)

    app.database = Database(db_path=app.config['DATABASE_PATH'])
    os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

    @app.cli.command('init-db')
    def init_db_command():
        """Create database tables that don't already exist yet."""
        app.database.init_db()
        click.echo('Initialized the database.')

    app.register_blueprint(tracks_bp)
    app.register_blueprint(web_bp)

    Swagger(app, template=build_swagger_template())

    return app

