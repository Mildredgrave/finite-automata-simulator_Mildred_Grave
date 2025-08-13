from flask import Flask

def create_app():
    app = Flask(__name__)

    # Register blueprint
    from .view.index import load_archive
    app.register_blueprint(load_archive)

    return app
