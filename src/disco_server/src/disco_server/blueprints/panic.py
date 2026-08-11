from flask import Blueprint

from disco_server import services

bp = Blueprint('panic', __name__, url_prefix='/api/panic')

@bp.route('/start', methods=['POST'])
def panic():
    """Activate panic mode.
    ---
    tags:
      - panic
    responses:
      200:
        description: Panic mode activated
    """
    panic = services.get_panic()
    panic.panic()
    return '', 200

@bp.route('/stop', methods=['POST'])
def panic_stop():
    """Stop panic mode.
    ---
    tags:
      - panic
    responses:
      200:
        description: Panic mode stopped
    """
    panic = services.get_panic()
    panic.stop()
    return '', 200
