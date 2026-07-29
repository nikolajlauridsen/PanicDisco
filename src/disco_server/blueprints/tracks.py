from flask import Blueprint, jsonify

from disco_server.services import get_track_library

bp = Blueprint('tracks', __name__, url_prefix='/api')


@bp.route('/tracks')
def list_tracks():
    library = get_track_library()
    return jsonify([track.name for track in library.get_tracks()])

@bp.route('/tracks/<int:track_id>', methods=['GET'])
def get_track(track_id):

    library = get_track_library()
    track = library.get_track(track_id)
    if track is None:
        return jsonify({'error': 'Track not found'}), 404

    return jsonify(track)