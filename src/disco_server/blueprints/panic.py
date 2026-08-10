from flask import Blueprint

from disco_server import services

bp = Blueprint('panic', __name__, url_prefix='/api/panic')

@bp.route('/start', methods=['POST'])
def panic():
    """Activate panic mode."""
    panic = services.get_panic()
    panic.panic()

@bp.route('/stop', methods=['POST'])
def panic_stop():
    """Stop panic mode."""
    panic = services.get_panic()
    panic.stop()
