import logging
import uuid
import datetime
from typing import Dict

from flask import make_response, request, render_template, redirect, url_for

from app.api.func import get_user_id_from_api_key, check_user_if_valid, set_state, check_password
from app.api.routes import set_door_state
from app.main import bp


SESSIONS = None
TIMEOUT = 300


def sessions() -> Dict[uuid.UUID, datetime.datetime]:
    global SESSIONS
    if SESSIONS is None:
        SESSIONS = {}
    return SESSIONS


def clean_sessions():
    return_dict = {}
    for session_id, timestamp in sessions().items():
        if (datetime.datetime.now(tz=datetime.timezone.utc) - timestamp) < datetime.timedelta(seconds=TIMEOUT):
            return_dict[session_id] = timestamp
    sessions().clear()
    sessions().update(return_dict)


def register_session(session_id: uuid.UUID) -> None:
    clean_sessions()
    if session_id not in sessions().keys():
        sessions()[session_id] = datetime.datetime.now(tz=datetime.timezone.utc)


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


@bp.route('/login', methods=['GET'])
def login_get():
    api_key = request.args.get('api-key')
    actor_id = request.args.get('actor-id')
    return render_template('login.html', api_key=api_key, actor_id=actor_id, msg=None)


@bp.route('/login', methods=['POST'])
def login_post():
    api_key = request.form.get('api-key')
    if api_key is None:
        return 'no api key'
    user_id = get_user_id_from_api_key(api_key)
    if user_id is None:
        return "wrong api key"
    actor_id = request.form.get('actor-id')
    if actor_id is None:
        return "no actor id"
    password = request.form.get('password')
    if not check_password(user_id, password):
        return render_template('login.html', msg='wrong password', **{'api_key': api_key, 'actor_id': actor_id})
    else:
        cookie = gen_cookie()
        clean_sessions()
        register_session(uuid.UUID(cookie))
        response = make_response(render_template('open.html', api_url=url_for('api.set_door_state'), **{'api_key': api_key, 'actor_id': actor_id}))
        response.set_cookie('SessionCookie', cookie)
        return response


def error(msg: str):
    return render_template('error.html', msg=msg)


@bp.route('/open', methods=['POST'])
def open_post():
    api_key = request.form.get('api-key')
    actor_id = request.form.get('actor-id')

    if request.cookies.get('SessionCookie') is not None:
        cookie = request.cookies.get('SessionCookie')
        try:
            cookie = uuid.UUID(cookie)
        except ValueError:
            return render_template('login.html', msg='please login first', **{'api_key': api_key, 'actor_id': actor_id})
        clean_sessions()
        if cookie not in sessions():
            return render_template('login.html', msg='please login first', **{'api_key': api_key, 'actor_id': actor_id})
        else:
            user_id = get_user_id_from_api_key(api_key)
            if user_id is None:
                return error('user id not found')
            else:
                try:
                    set_state(uuid.UUID(request.form.get('actor-id')), user_id)
                    return render_template('open.html', msg='Success!', **{'api_key': api_key, 'actor_id': actor_id})

                except ValueError:
                    return error('actor id malformed')
                except PermissionError:
                    return error('no permission')
    else:
        return render_template('login.html', msg='please login first', **{'api_key': api_key, 'actor_id': actor_id})


@bp.route('/open', methods=['GET'])
def open_get():
    api_key = request.args.get('api-key')
    actor_id = request.args.get('actor-id')
    return render_template('open.html', **{'api_key': api_key, 'actor_id': actor_id})


@bp.route('/health')
def health():
    return 200, {'status': 'UP'}
