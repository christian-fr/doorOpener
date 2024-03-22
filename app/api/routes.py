import json
import uuid
from json import JSONDecodeError
from typing import Optional

from flask import request

from app.api.util import get_state, set_state, log, add_user, add_scope, add_valid
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


@bp.route('/setState', methods=['GET'])
def set_door_state():
    if request.args.get('api-key') is None:
        log(f'key not found')
        return Response(
            response=json.dumps({'msg': 'no key provided'}),
            status=403,
            mimetype='application/json'
        )
    elif request.args.get('actors') is None:
        return Response(
            response=json.dumps({'msg': 'no actors list provided'}),
            status=403,
            mimetype='application/json'
        )
    else:
        try:
            _ = json.loads(request.args.get('actors'))
        except JSONDecodeError:
            log(f'JSONDecodeError while handling actors string: {dict(request.args)}')
            return Response(
                response=json.dumps({'msg': 'no actors list provided'}),
                status=403,
                mimetype='application/json'
            )
        result = set_state(json.loads(request.args.get('actors')), request.args.get('api-key'))
        return Response(
            response=json.dumps(result[1]),
            status=result[0],
            mimetype='application/json'
        )


@bp.route('/getState', methods=['GET'])
def get_door_state():
    if request.args.get('api-key') is None:
        log(f'key not found')
        return Response(
            response=json.dumps({'msg': 'no key provided'}),
            status=403,
            mimetype='application/json'
        )
    elif request.args.get('actors') is None:
        return Response(
            response=json.dumps({'msg': 'no actors list provided'}),
            status=403,
            mimetype='application/json'
        )
    else:
        try:
            _ = json.loads(request.args.get('actors'))
        except JSONDecodeError:
            log(f'JSONDecodeError while handling actors string: {dict(request.args)}')
            return Response(
                response=json.dumps({'msg': 'no actors list provided'}),
                status=403,
                mimetype='application/json'
            )
        result = get_state(json.loads(request.args.get('actors')), request.args.get('api-key'))
        return Response(
            response=json.dumps(result[1]),
            status=result[0],
            mimetype='application/json'
        )


def json_response(status: int, msg: str, response: Optional[dict] = None) -> Response:
    if response is None:
        response = {}
    Response(
        response=json.dumps({**response, 'msg': msg}),
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
            log(f'unkown role: {request.args.get('role')}')
            return json_response(404, 'role unkown')

        result = add_user(request.args.get('api-key'), request.args.get('name'), role)
        return Response(
            response=json.dumps(result[1]),
            status=result[0],
            mimetype='application/json'
        )


@bp.route('/addValid', methods=['GET'])
def api_add_valid():
    if request.args.get('api-key') is None:
        return json_response(403, 'key missing')
    elif request.args.get('user-id') is None:
        return json_response(404, 'user-id missing')
    elif request.args.get('start') is None:
        return json_response(404, 'start missing')
    elif request.args.get('end') is None:
        return json_response(404, 'end missing')
    else:
        result = add_valid(request.args.get('api-key'), uuid.UUID(request.args.get('user-id')),
                           request.args.get('start'), request.args.get('end'), )
        return Response(
            response=json.dumps(result[1]),
            status=result[0],
            mimetype='application/json'
        )


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
            log(f'unkown mode: {mode}')
            return json_response(404, 'mode unkown')

        result = add_scope(api_key, uuid.UUID(user_id), uuid.UUID(actor_id), mode)
        return Response(
            response=json.dumps(result[1]),
            status=result[0],
            mimetype='application/json'
        )


@bp.route('/createApiKey', methods=['GET'])
def create_api_key():
    if request.args.get('api-key') is None:
        return 'key missing'
    elif request.args.get('user-id') is None:
        return 'user-id missing'
    else:
        raise NotImplementedError()
        result = create_api_key_helper(request.args.get('api-key'), request.args.get('user-id'))
        return Response(
            response=json.dumps(result[1]),
            status=result[0],
            mimetype='application/json'
        )


@bp.route('/listApiKeys', methods=['GET'])
def list_api_keys():
    if request.args.get('api-key') is None:
        return 'key missing'
    else:
        raise NotImplementedError()
        result = list_api_keys_helper(request.args.get('api-key'))
        return Response(
            response=json.dumps(result[1]),
            status=result[0],
            mimetype='application/json'
        )


@bp.route('/setScope', methods=['GET'])
def set_scope():
    raise NotImplementedError()

    if request.args.get('api-key') is None:
        return 'api-key missing'
    elif request.args.get('user-id') is None:
        return 'user-id missing'
    elif request.args.get('actor-id') is None:
        return 'actor-id missing'
    elif request.args.get('mode') is None:
        return 'mode missing'
    else:
        user_id = request.args.get('user-id')
        actor_id = request.args.get('actor-id')

        if actor_id not in user_db().keys():
            return 400, 'actor not found'
        elif user_db()[actor_id]['role'] != Role.actor:
            return 400, 'user with user-id is not an actor'
        else:
            all_permissions_for_user_actor = {k: v for k, v in permission_db().items() if
                                              v['user_id'] == user_id and v['actor_id'] == actor_id}
            if all_permissions_for_user_actor == {}:
                key_to_modify = uuid.uuid4().hex
            else:
                key_to_modify = list(all_permissions_for_user_actor.keys())[0]
            # clean up
            [permission_db().pop(k) for k in list(all_permissions_for_user_actor.keys())[1:]]
            permission_db()[key_to_modify] = {'user_id': request.args.get('user-id'),
                                              'actor_id': request.args.get('actor-id'),
                                              'mode': request.args.get('mode')}

            return Response(
                response=json.dumps({'msg': 'permission modified', 'permission-id': key_to_modify}),
                status=200,
                mimetype='application/json'
            )
