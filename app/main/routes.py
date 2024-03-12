from app.main import bp


@bp.route('/')
def index():
    return 'This is The Main Blueprint'

@bp.route('/health')
def health():
    return 200, {'status': 'UP'}
