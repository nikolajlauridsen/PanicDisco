import os

import click
from flasgger import Swagger
from flask import Flask

from disco_server.blueprints.tracks import bp as tracks_bp
from disco_server.blueprints.web import bp as web_bp
from disco_server.blueprints.boombox import bp as boombox_bp
from disco_server.blueprints.panic import bp as panic_bp
from disco_server.core.actions.music_action import MusicAction
from disco_server.core.database.database import Database
from disco_server.services import add_panic_action, get_last_played, get_boombox
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
        VLC_ARGS='',
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

    register_blueprints(app)
    Swagger(app, template=build_swagger_template())

    with app.app_context():
        add_panic_actions()
        initialize_boombox(app)

    return app


def register_blueprints(app: Flask):
    app.register_blueprint(tracks_bp)
    app.register_blueprint(web_bp)
    app.register_blueprint(boombox_bp)
    app.register_blueprint(panic_bp)

def add_panic_actions() -> None:
    """Register the built-in panic actions.

    Extend this to register additional `PanicAction` implementations (e.g.
    a GPIO-driven lights action) alongside `MusicAction`.
    """
    add_panic_action(MusicAction())

def initialize_boombox(app: Flask) -> None:
    """Reload whatever track was loaded when the server last stopped, if any.

    No-ops if the database hasn't been initialized yet (a brand new database
    file, or `flask init-db`'s own app-factory bootstrap, both run through
    this same `create_app()` before any table necessarily exists) — there's
    nothing to restore in that case anyway.
    """
    if not app.database.is_initialized():
        return

    last_played = get_last_played().get()
    if last_played is not None:
        get_boombox().load_track(last_played)

