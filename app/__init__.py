from flask import  Flask

def app():
    app = Flask(__name__)

    from .view.index import loadarchive

    app.register_blueprint(loadarchive)

    return app