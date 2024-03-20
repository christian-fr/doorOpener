import json
import uuid
from json import JSONDecodeError

from flask import request

from app.api.util import get_state, set_state, log
from app.models.users import Role

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


@bp.route('/createUser', methods=['GET'])
def create_user():
    raise NotImplementedError

    if request.args.get('api-key') is None:
        return 'key missing'
    elif request.args.get('name') is None:
        return 'name missing'
    elif request.args.get('role') is None:
        return 'role missing'
    else:

        if request.args.get('user-id') is not None:
            user_id = request.args.get('user-id')
        else:
            user_id = str(uuid.uuid4())

        try:
            role = Role[request.args.get('role')]
        except KeyError:
            log(f'unkown role: {request.args.get('role')}')
            return 'role unkown'

        try:
            timeout = int(request.args.get('timeout')) if request.args.get('timeout') is not None else None
        except ValueError:
            log(f'invalid timeout: {request.args.get('timeout')}')
            return 'invalid timeout value'

        result = create_user_helper(request.args.get('api-key'), request.args.get('name'), role, user_id, timeout)
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
