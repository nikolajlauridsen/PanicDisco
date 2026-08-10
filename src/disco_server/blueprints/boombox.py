from flask import Blueprint, jsonify

from disco_server.services import get_track_library, get_boombox, get_last_played
from disco_server.web.view_models.response_models.error import Error
bp = Blueprint('boombox', __name__, url_prefix='/api/boombox')

# TODO: Move somewhere shared.
def not_found():
    return jsonify(Error("Track not found", 404)), 404

def not_loaded():
    return jsonify(Error("Track not loaded", 503)), 503

@bp.route('/load/<int:track_id>', methods=['PUT'])
def load_track(track_id):
    """Load a track into the boombox.
    ---
    tags:
      - boombox
    parameters:
      - name: track_id
        in: path
        type: integer
        required: true
    responses:
      200:
        description: Track loaded
      404:
        description: Track not found
        schema:
          $ref: '#/definitions/Error'
    """
    library = get_track_library()
    track = library.get_track(track_id)
    if track is None:
        return not_found()

    boombox = get_boombox()
    last_played = get_last_played()
    boombox.load_track(track)
    last_played.set(track)
    return '', 200

@bp.route('/play', methods=['PUT'])
def play():
    """Start playback of the loaded track.
    ---
    tags:
      - boombox
    responses:
      200:
        description: Playback started
      503:
        description: No track is loaded
        schema:
          $ref: '#/definitions/Error'
    """
    boombox = get_boombox()
    if not boombox.is_loaded():
        return not_loaded()

    boombox.play()
    return '', 200

@bp.route('/stop', methods=['PUT'])
def stop():
    """Stop playback of the loaded track.
    ---
    tags:
      - boombox
    responses:
      200:
        description: Playback stopped
      503:
        description: No track is loaded
        schema:
          $ref: '#/definitions/Error'
    """
    boombox = get_boombox()
    if not boombox.is_loaded():
        return not_loaded()

    boombox.stop()
    return '', 200

@bp.route('/pause', methods=['PUT'])
def pause():
    """Pause playback of the loaded track.
    ---
    tags:
      - boombox
    responses:
      200:
        description: Playback paused
      503:
        description: No track is loaded
        schema:
          $ref: '#/definitions/Error'
    """
    boombox = get_boombox()
    if not boombox.is_loaded():
        return not_loaded()

    boombox.pause()
    return '', 200

@bp.route('/resume', methods=['PUT'])
def resume():
    """Resume playback of the loaded track.
    ---
    tags:
      - boombox
    responses:
      200:
        description: Playback resumed
      503:
        description: No track is loaded
        schema:
          $ref: '#/definitions/Error'
    """
    boombox = get_boombox()
    if not boombox.is_loaded():
        return not_loaded()

    boombox.resume()
    return '', 200