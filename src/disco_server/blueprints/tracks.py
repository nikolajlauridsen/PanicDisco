import os.path
import uuid

from flask import Blueprint, current_app, jsonify, request, url_for

from disco_server.core.models.track import Track
from disco_server.services import get_track_library
from disco_server.web.mapping import mapper
from disco_server.web.view_models.request_models.track_update import TrackUpdate
from disco_server.web.view_models.request_models.track_upload import TrackUpload
from disco_server.web.view_models.response_models.error import Error

bp = Blueprint('tracks', __name__, url_prefix='/api')

def not_found():
    return jsonify(Error("Track not found", 404)), 404

@bp.route('/tracks')
def list_tracks():
    """List all track names.
    ---
    tags:
      - tracks
    responses:
      200:
        description: Track names
        schema:
          type: array
          items:
            type: string
    """
    library = get_track_library()
    return jsonify([track.name for track in library.get_tracks()])

@bp.route('/tracks/<int:track_id>', methods=['GET'])
def get_track(track_id):
    """Get details for a single track.
    ---
    tags:
      - tracks
    parameters:
      - name: track_id
        in: path
        type: integer
        required: true
    responses:
      200:
        description: Track details
        schema:
          $ref: '#/definitions/TrackDetails'
      404:
        description: Track not found
        schema:
          $ref: '#/definitions/Error'
    """
    library = get_track_library()
    track = library.get_track(track_id)
    if track is None:
        return not_found()

    return jsonify(mapper.map_to_track_details(track))

@bp.route('/tracks/<int:track_id>', methods=['PUT'])
def update_track(track_id):
    """Update a track's name, cue point and path.
    ---
    tags:
      - tracks
    parameters:
      - name: track_id
        in: path
        type: integer
        required: true
      - name: body
        in: body
        required: true
        schema:
          $ref: '#/definitions/TrackUpdate'
    responses:
      204:
        description: Track updated
      404:
        description: Track not found
        schema:
          $ref: '#/definitions/Error'
    """
    library = get_track_library()
    track_update = TrackUpdate.model_validate(request.json)
    track = mapper.map_to_track(track_update)

    if not library.update_track(track_id, track):
        return not_found()
    return '', 204

@bp.route('/tracks/<int:track_id>', methods=['DELETE'])
def delete_track(track_id):
    """Delete a track.
    ---
    tags:
      - tracks
    parameters:
      - name: track_id
        in: path
        type: integer
        required: true
    responses:
      204:
        description: Track deleted
      404:
        description: Track not found
        schema:
          $ref: '#/definitions/Error'
    """
    library = get_track_library()
    track = library.get_track(track_id)
    if track is None:
        return not_found()

    library.delete_track(track)
    return '', 204

@bp.route('/tracks/upload', methods=['POST'], )
def upload_track():
    format = request.files['file'].name.split('.')[-1]
    if format != 'mp3':
        return jsonify(Error('File format not supported', 400)), 400

    track_upload = TrackUpload(request.form)
    path = os.path.join(current_app.config['UPLOAD_FOLDER'], f"{uuid.uuid4().hex}.{format}")

    track = Track(
        name=track_upload.name,
        path=path,
        cue_time=track_upload.cue_point)

    library = get_track_library()
    library.create_track(track)
    request.files['file'].save(path)

    return None, 201, {'Location': url_for('tracks.get_track', track_id=track.id)}
