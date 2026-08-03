from flask import Blueprint, render_template

from disco_server.services import get_track_library

bp = Blueprint('web', __name__)

@bp.route('/')
def index():
    library = get_track_library()
    return render_template('tracks.html', tracks=library.get_tracks())
