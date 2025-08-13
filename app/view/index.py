from flask import Blueprint,request

archive = Blueprint('archive', __name__, url_prefix='/')

@archive.route('/')

def index():
    return "Welcome to the Finite Automata Simulator!"


@archive.route('/archive/', methods=['POST'])
def archive_post():

    if request.is_json:
        data = request.get_json()
        print(data)

    