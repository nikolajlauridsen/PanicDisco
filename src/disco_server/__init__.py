import os

from flask import Flask

def create_app():
    app = Flask(__name__, instance_relative_config=True)

    print(f"Instance path {app.instance_path}")
    os.makedirs(app.instance_path, exist_ok=True)

    @app.route('/hello')
    def hello():
        return 'Hello, World!'

    return app

