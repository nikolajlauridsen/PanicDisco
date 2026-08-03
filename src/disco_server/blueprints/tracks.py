import os.path
import uuid

from flask import Blueprint, current_app, jsonify, request, send_from_directory, url_for
from pydantic import ValidationError

from disco_server.core.services import file_manager
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
    """List all tracks.
    ---
    tags:
      - tracks
    responses:
      200:
        description: Tracks
        schema:
          type: array
          items:
            $ref: '#/definitions/TrackEntity'
    """
    library = get_track_library()
    return jsonify([mapper.map_to_track_entity(track) for track in library.get_tracks()])

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

@bp.route('/tracks/<int:track_id>/file', methods=['GET'])
def get_track_file(track_id):
    """Serve the audio file for a track, for preview/playback.
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
        description: The track's audio file
        schema:
          type: file
      404:
        description: Track not found, or its file is missing
        schema:
          $ref: '#/definitions/Error'
    """
    library = get_track_library()
    track = library.get_track(track_id)
    if track is None:
        return not_found()

    upload_folder = current_app.config['UPLOAD_FOLDER']
    filename = os.path.basename(track.path)
    if not os.path.isfile(os.path.join(upload_folder, filename)):
        return not_found()

    return send_from_directory(upload_folder, filename)

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

    file_manager.remove(track.path)
    library.delete_track(track)
    return '', 204

@bp.route('/tracks/upload', methods=['POST'], )
def upload_track():
    """Upload an mp3 file and create a track from it.
    ---
    tags:
      - tracks
    consumes:
      - multipart/form-data
    parameters:
      - name: file
        in: formData
        type: file
        required: true
        description: The mp3 file to upload.
      - name: name
        in: formData
        type: string
        required: true
      - name: cue_point
        in: formData
        type: integer
        required: true
    responses:
      201:
        description: Track created
        headers:
          Location:
            type: string
            description: URL of the created track
      400:
        description: No file uploaded, unsupported file format, or invalid track metadata
        schema:
          $ref: '#/definitions/Error'
    """
    file = request.files.get('file')
    if file is None:
        return jsonify(Error('No file uploaded', 400)), 400

    format = file.filename.split('.')[-1]
    if format not in ['mp3', 'flac', 'wav']:
        return jsonify(Error('File format not supported', 400)), 400

    try:
        track_upload = TrackUpload.model_validate(request.form.to_dict())
    except ValidationError:
        return jsonify(Error('Invalid track metadata', 400)), 400

    path = os.path.join(current_app.config['UPLOAD_FOLDER'], f"{uuid.uuid4().hex}.{format}")

    library = get_track_library()
    track = mapper.map_upload_to_track(track_upload, path)
    library.create_track(track)
    file_manager.save(file, path)

    return '', 201, {'Location': url_for('tracks.get_track', track_id=track.id)}
