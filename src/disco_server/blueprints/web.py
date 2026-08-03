from flask import Blueprint, render_template

from disco_server.services import get_track_library

bp = Blueprint('web', __name__)

@bp.app_template_filter('cue_point')
def format_cue_point(seconds):
    """Format a cue point (in seconds) as minutes:seconds, e.g. 65 -> '1:05'."""
    if seconds is None:
        return '—'
    minutes, secs = divmod(seconds, 60)
    return f'{minutes}:{secs:02d}'

@bp.route('/')
def index():
    library = get_track_library()
    return render_template('tracks.html', tracks=library.get_tracks())

@bp.route('/upload')
def upload():
    return render_template('upload.html')
