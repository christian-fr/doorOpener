import datetime
import json
import traceback
import uuid
from typing import Optional

from flask import request
from werkzeug.exceptions import UnsupportedMediaType

from app.api.func import get_state, set_state, log, add_user, add_scope, add_valid, check_if_admin_by_api_key, \
    get_user_id_from_api_key, get_role_from_user_id, health_check_actor, regenerate_api_key
from app.models.scope import Mode
from app.models.user import Role

from app.api import bp
from flask import Response


@bp.route('/', methods=['GET'])
def index_get():
    return Response(
        response=json.dumps({'msg': 'This is the api endpoint.'}),
        status=200,
        mimetype='application/json'
    )


@bp.route('/setState', methods=['POST'])
def set_door_state():
    try:
        if request.json != {}:
            api_key = request.json.get('api-key')
            actor_id = request.json.get('actor-id')
            if api_key is None:
                log(f'key not found')
                return Response(
                    response=json.dumps({'msg': 'no key provided'}),
                    status=403,
                    mimetype='application/json'
                )
            elif actor_id is None:
                return Response(
                    response=json.dumps({'msg': 'no actor id provided'}),
                    status=403,
                    mimetype='application/json'
                )
            user_id = get_user_id_from_api_key(request.json.get('api-key'))
        else:
            api_key = request.form.get('api-key')
            actor_id = request.form.get('actor-id')
            if api_key is None:
                log(f'key not found')
                return Response(
                    response=json.dumps({'msg': 'no key provided'}),
                    status=403,
                    mimetype='application/json'
                )
            elif actor_id is None:
                return Response(
                    response=json.dumps({'msg': 'no actor id provided'}),
                    status=403,
                    mimetype='application/json'
                )
            user_id = get_user_id_from_api_key(request.form.get('api-key'))
    except UnsupportedMediaType:
        api_key = request.form.get('api-key')
        actor_id = request.form.get('actor-id')
        if api_key is None:
            log(f'key not found')
            return Response(
                response=json.dumps({'msg': 'no key provided'}),
                status=403,
                mimetype='application/json'
            )
        elif actor_id is None:
            return Response(
                response=json.dumps({'msg': 'no actor id provided'}),
                status=403,
                mimetype='application/json'
            )
        user_id = get_user_id_from_api_key(request.form.get('api-key'))

    if user_id is None:
        return response_permission_error()
    else:
        try:
            set_state(uuid.UUID(actor_id), user_id)
            return response_success()

        except ValueError:
            return response_input_error()
        except PermissionError:
            return response_permission_error()


@bp.route('/getState', methods=['GET'])
def get_door_state():
    if request.args.get('api-key') is None:
        log(f'key not found')
        return Response(
            response=json.dumps({'msg': 'no key provided'}),
            status=403,
            mimetype='application/json'
        )
    elif request.args.get('actor-id') is None:
        return Response(
            response=json.dumps({'msg': 'no actor id provided'}),
            status=403,
            mimetype='application/json'
        )
    else:
        user_id = get_user_id_from_api_key(request.args.get('api-key'))
        if user_id is None:
            return response_permission_error()
        else:
            try:
                result = get_state(uuid.UUID(request.args.get('actor-id')), user_id)
                if result is None:
                    return response_permission_error()
                else:
                    return json_response(200, None, {'state': result})

            except ValueError:
                return response_input_error()
            except PermissionError:
                return response_permission_error()


@bp.route('/actorHealth', methods=['GET'])
def check_actor_health():
    if request.args.get('api-key') is None:
        log(f'key not found')
        return Response(
            response=json.dumps({'msg': 'no key provided'}),
            status=403,
            mimetype='application/json'
        )
    elif request.args.get('actor-id') is None:
        return Response(
            response=json.dumps({'msg': 'no actor id provided'}),
            status=403,
            mimetype='application/json'
        )
    elif request.args.get('timeout') is None:
        return Response(
            response=json.dumps({'msg': 'no timeout provided'}),
            status=403,
            mimetype='application/json'
        )
    else:
        user_id = get_user_id_from_api_key(request.args.get('api-key'))
        if user_id is None:
            return response_permission_error()
        else:
            role = get_role_from_user_id(user_id)
            if role != Role.maintenance:
                return Response(
                    response=json.dumps({'msg': 'api key is not from maintenance user'}),
                    status=403,
                    mimetype='application/json'
                )
            else:
                try:
                    actor_id = uuid.UUID(request.args.get('actor-id'))
                    return Response(
                        response=json.dumps({'health': health_check_actor(actor_id, int(request.args.get('timeout')))}),
                        status=200,
                        mimetype='application/json'
                    )
                except ValueError:
                    return response_input_error()
                except PermissionError:
                    return response_permission_error()


def json_response(status: int, msg: Optional[str], response: Optional[dict] = None) -> Response:
    if response is None:
        response = {}
    message = {}
    if msg is not None:
        message = {'msg': msg}
    return Response(
        response=json.dumps({**response, **message}),
        status=status,
        mimetype='application/json'
    )


@bp.route('/addUser', methods=['GET'])
def api_add_user():
    if request.args.get('api-key') is None:
        return json_response(403, 'key missing')
    elif request.args.get('name') is None:
        return json_response(404, 'name missing')
    elif request.args.get('role') is None:
        return json_response(404, 'role missing')
    else:
        try:
            role = Role[request.args.get('role')]
        except KeyError:
            log(f"unknown role: {request.args.get('role')}")
            return json_response(404, 'role unknown')
        if check_if_admin_by_api_key(request.args.get('api-key')):
            result = add_user(request.args.get('name'), role=role, password=request.args.get('password'))
            return json_response(200, None, result)
        else:
            return json_response(403, 'permission_error')


@bp.route('/regenerateApiKey', methods=['GET'])
def api_regenerate_api_key():
    if request.args.get('api-key') is None:
        return json_response(403, 'key missing')
    else:
        user_id = get_user_id_from_api_key(request.args.get('api-key'))
        if user_id is None:
            return json_response(403, 'unknown api key')
        new_api_key = regenerate_api_key(user_id)
        return json_response(200, None, new_api_key)


def response_permission_error():
    return json_response(403, 'permission error')


def response_input_error():
    return json_response(403, 'bad input error')


def response_success():
    return json_response(200, 'success')


def ts_from_iso_or_none(iso_string: Optional[str]) -> Optional[datetime.datetime]:
    if iso_string is not None:
        return datetime.datetime.fromisoformat(iso_string)
    else:
        return None


@bp.route('/addValid', methods=['GET'])
def api_add_valid():
    if request.args.get('api-key') is None:
        return json_response(403, 'key missing')
    elif request.args.get('user-id') is None:
        return json_response(404, 'user-id missing')
    else:
        start = ts_from_iso_or_none(request.args.get('start'))
        end = ts_from_iso_or_none(request.args.get('end'))
        if not check_if_admin_by_api_key(request.args.get('api-key')):
            return response_permission_error()

        add_valid(uuid.UUID(request.args.get('user-id')), start, end, )
        return response_success()


@bp.route('/addScope', methods=['GET'])
def api_add_scope():
    api_key = request.args.get('api-key')
    user_id = request.args.get('user-id')
    actor_id = request.args.get('actor-id')
    mode = request.args.get('mode')

    if api_key is None:
        return json_response(403, 'key missing')
    elif user_id is None:
        return json_response(404, 'user id missing')
    elif actor_id is None:
        return json_response(404, 'actor id missing')
    elif mode is None:
        return json_response(404, 'mode missing')
    else:
        try:
            mode = Mode[mode]
        except KeyError:
            log(f'unknown mode: {mode}')
            return json_response(404, 'mode unknown')
        if not check_if_admin_by_api_key(api_key):
            return json_response(403, 'invalid api key')
        try:
            add_scope(uuid.UUID(user_id), uuid.UUID(actor_id), mode)
        except ValueError as e:
            return json_response(400, 'badly formed uuid string')
        return json_response(200, 'success')
