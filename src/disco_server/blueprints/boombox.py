from flask import Blueprint, jsonify

from disco_server.services import get_track_library, get_boombox
from disco_server.web.view_models.response_models.error import Error
bp = Blueprint('boombox', __name__, url_prefix='/api/boombox')

# TODO: Move somewhere shared.
def not_found():
    return jsonify(Error("Track not found", 404)), 404

def not_loaded():
    return jsonify(Error("Track not loaded", 503)), 503

@bp.route('/load/<int:track_id>', methods=['PUT'])
def load_track(track_id):
    library = get_track_library()
    track = library.get_track(track_id)
    if track is None:
        return not_found()

    boombox = get_boombox()
    boombox.load_track(track)
    return '', 200

@bp.route('/play', methods=['PUT'])
def play():
    boombox = get_boombox()
    if not boombox.is_loaded():
        return not_loaded()

    boombox.play()
    return '', 200

@bp.route('/stop', methods=['PUT'])
def stop():
    boombox = get_boombox()
    if not boombox.is_loaded():
        return not_loaded()

    boombox.stop()
    return '', 200

@bp.route('/pause', methods=['PUT'])
def pause():
    boombox = get_boombox()
    if not boombox.is_loaded():
        return not_loaded()

    boombox.pause()
    return '', 200

@bp.route('/resume', methods=['PUT'])
def resume():
    boombox = get_boombox()
    if not boombox.is_loaded():
        return not_loaded()

    boombox.resume()
    return '', 200