from flask import Blueprint, jsonify, request

from disco_server.services import get_track_library
from disco_server.web.mapping import mapper
from disco_server.web.view_models.request_models.track_update import TrackUpdate
from disco_server.web.view_models.response_models.error import Error

bp = Blueprint('tracks', __name__, url_prefix='/api')

def not_found():
    return jsonify(Error("Track not found", 404)), 404

@bp.route('/tracks')
def list_tracks():
    library = get_track_library()
    return jsonify([track.name for track in library.get_tracks()])

@bp.route('/tracks/<int:track_id>', methods=['GET'])
def get_track(track_id):
    library = get_track_library()
    track = library.get_track(track_id)
    if track is None:
        return not_found()

    return jsonify(mapper.map_to_track_details(track))

@bp.route('/tracks/<int:track_id>', methods=['PUT'])
def update_track(track_id):
    library = get_track_library()
    track_update = TrackUpdate.model_validate(request.json)
    track = mapper.map_to_track(track_update)

    if not library.update_track(track_id, track):
        return not_found()
    return '', 204
