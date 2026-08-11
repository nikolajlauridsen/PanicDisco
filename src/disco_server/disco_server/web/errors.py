from flask import jsonify

from disco_shared.models.error import Error


def not_found():
    """Return the shared 404 response for 'no such track'."""
    return jsonify(Error("Track not found", 404)), 404


def not_loaded():
    """Return the shared 503 response for 'no track is currently loaded'."""
    return jsonify(Error("Track not loaded", 503)), 503
