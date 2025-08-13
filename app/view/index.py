from flask import Blueprint,request
from ..services.service import Archive

loadarchive = Blueprint('loadarchive', __name__, url_prefix='/')

@loadarchive.route('/')
def index():
    return "Welcome to the Finite Automata Simulator!"


@loadarchive.route('/archive/', methods=['POST'])
def archive_post():
    data = request.files.get('file')

    response = Archive(data)

    return response.initializer()


    