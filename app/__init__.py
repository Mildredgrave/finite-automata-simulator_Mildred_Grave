from flask import  Flask

def app():
    app = Flask(__name__)

    from .view.index import archive

    app.register_blueprint(archive)

    return app