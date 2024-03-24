import logging
import uuid

from flask import make_response, request

from app.main import bp


def gen_cookie() -> str:
    return str(uuid.uuid4())


@bp.route('/')
def index():
    response = make_response('This is the main blueprint.')

    if request.cookies.get('SessionCookie') is not None:
        request.cookies.get('SessionCookie')
        logging.info('cookie found' + request.cookies.get('SessionCookie'))
    else:
        cookie = gen_cookie()
        response.set_cookie('SessionCookie', cookie)
        logging.info('cookie generated' + cookie)
    return response


@bp.route('/health')
def health():
    return 200, {'status': 'UP'}
