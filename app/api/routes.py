import json
import os.path
import uuid
import datetime
from typing import Optional, List, Tuple, Dict, Union

from flask import request
from sqlalchemy import select
from sqlalchemy.exc import IntegrityError, StatementError

from app.models.users import Users, Role
from app.models.scope import Scope
from app.models.state import State
from app.models.valid import Valid

from app.api import bp
from app.extensions import db
from flask import Response


def generate_new_key():
    new_key = None
    while new_key is None or new_key in keys_db():
        new_key = str(uuid.uuid4())
    return new_key


def create_user_key(user_id: str):
    if user_id not in user_db():
        log(f'{user_id=} not found in user_db()')
        return 403, {'msg': 'db error'}
    new_key = generate_new_key()
    keys_db()[new_key] = {'user_id': user_id}
    return 200, {'msg': 'key created', 'api-key': new_key}


def get_state(actor_id_list: List[str], key: str) -> Tuple[int, dict]:
    if check_and_increment():
        sanitize_state_db()
    if not isinstance(actor_id_list, list):
        return 400, {'msg': 'actor ids not a list'}
    if key not in keys_db():
        log(f'key "{key}" not found')
        return 400, {'msg': 'permission denied'}
    else:
        if 'user_id' not in keys_db()[key]:
            log(f'db error: "ref_id" not found in keys_db()[key]: "{keys_db()[key]}"')
            return 403, {'msg': 'db error'}
        else:
            user_id = keys_db()[key]['user_id']

            if 'role' not in user_db()[user_id]:
                log(f'db error: "type" not in {user_db()[user_id]=}"]')
                return 403, {'msg': 'db error'}
            else:
                if user_db()[user_id]['role'] in [Role.ACTOR]:
                    if check_valid(user_id):
                        msg = {}
                        allowed_actors = get_all_actors(user_id, 'r')
                        for actor_id in actor_id_list:
                            if actor_id not in allowed_actors:
                                msg[actor_id] = 403, {'msg': 'permission denied'}
                        for actor_id in allowed_actors:
                            if actor_id not in actor_id_list:
                                continue
                            else:
                                msg[actor_id] = get_actor_state(actor_id)
                        return 200, msg
                    else:
                        log(f'permission error: user not valid: {user_id} // '
                            f'{[v for v in valid_db().values() if v["user_id"] == user_id]}')
                        return 403, {'msg': 'permission error'}

                else:
                    log(f'db error: unallowed role: {user_db()[user_id]['role']=}')
                    return 403, {'msg': 'db error'}


def list_api_keys_helper(admin_api_key: str) -> Tuple[int, Dict[str, Union[List[str], str]]]:
    if admin_api_key not in keys_db():
        return 403, {'msg': 'permission error'}
    else:
        user_id = keys_db()[admin_api_key]['user_id']
        if user_db()[user_id]['role'] != Role.ADMIN:
            return 403, {'msg': 'permission error'}
        else:
            return 200, {'api-keys-truncated': [k[:6] for k in keys_db().keys() if k != admin_api_key]}


def create_user_helper(api_key: str, name: str, role: Role, user_id: Optional[str] = None,
                       timeout: Optional[int] = None, valid_from: datetime.datetime = None,
                       valid_until: datetime.datetime = None) -> Tuple[int, Union[Dict[str, str], str]]:
    if 'user_id' is None:
        user_id = uuid.uuid4().hex
    if api_key in keys_db():
        api_user_id = keys_db()[api_key]['user_id']
        if user_db()[api_user_id]['role'] == Role.ADMIN:
            if user_id in user_db():
                return 400, 'user id already present'
            else:
                if valid_from is not None and valid_until is not None:
                    if valid_from > valid_until:
                        return 400, 'valid-from and valid-until invalid'

                if role in [Role.USER, Role.DISABLED]:
                    timeout = None
                user_db()[user_id] = {'name': name, 'role': role, 'timeout': timeout, 'valid_from': valid_from,
                                      'valid_until': valid_until}
                return 200, {'msg': 'user created', 'user-id': user_id}
        else:
            return 403, 'permission error'


def create_api_key_helper(api_key: str, user_id: str) -> Tuple[int, Union[Dict[str, str], str]]:
    if api_key in keys_db():
        api_user_id = keys_db()[api_key]['user_id']
        if user_db()[api_user_id]['role'] == Role.ADMIN:
            if user_id not in user_db():
                return 403, 'user id not found'
            else:
                api_key = gen_api_key()
                keys_db()[api_key] = {'user_id': user_id}
                return 200, {'msg': 'api key generated', 'api-key': api_key}
        else:
            return 403, 'permission error'


def gen_api_key() -> str:
    return os.urandom(32).hex()


def get_entry_or_none(data: dict, key: str) -> Optional[str]:
    if key in data.keys():
        result = data[key]
        assert isinstance(result, str)
        if result.strip() == '':
            return None
        return result
    else:
        return None


@bp.route('/', methods=['GET'])
def index_get():
    return Response(
        response=json.dumps({'msg': 'This is the api endpoint.'}),
        status=200,
        mimetype='application/json'
    )


@bp.route('/setDoorState', methods=['GET'])
def set_door_state():
    if request.args.get('api-key') is None:
        log(f'key not found')
        return app.response_class(
            response=json.dumps({'msg': 'no key provided'}),
            status=403,
            mimetype='application/json'
        )
    elif request.args.get('actors') is None:
        return app.response_class(
            response=json.dumps({'msg': 'no actors list provided'}),
            status=403,
            mimetype='application/json'
        )
    else:
        try:
            _ = json.loads(request.args.get('actors'))
        except JSONDecodeError:
            log(f'JSONDecodeError while handling actors string: {dict(request.args)}')
            return app.response_class(
                response=json.dumps({'msg': 'no actors list provided'}),
                status=403,
                mimetype='application/json'
            )
        result = set_state(json.loads(request.args.get('actors')), request.args.get('api-key'))
        return app.response_class(
            response=json.dumps(result[1]),
            status=result[0],
            mimetype='application/json'
        )


@bp.route('/getDoorState', methods=['GET'])
def get_door_state():
    if request.args.get('api-key') is None:
        log(f'key not found')
        return app.response_class(
            response=json.dumps({'msg': 'no key provided'}),
            status=403,
            mimetype='application/json'
        )
    elif request.args.get('actors') is None:
        return app.response_class(
            response=json.dumps({'msg': 'no actors list provided'}),
            status=403,
            mimetype='application/json'
        )
    else:
        try:
            _ = json.loads(request.args.get('actors'))
        except JSONDecodeError:
            log(f'JSONDecodeError while handling actors string: {dict(request.args)}')
            return app.response_class(
                response=json.dumps({'msg': 'no actors list provided'}),
                status=403,
                mimetype='application/json'
            )
        result = get_state(json.loads(request.args.get('actors')), request.args.get('api-key'))
        return app.response_class(
            response=json.dumps(result[1]),
            status=result[0],
            mimetype='application/json'
        )


@bp.route('/createUser', methods=['GET'])
def create_user():
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
        return app.response_class(
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
        result = create_api_key_helper(request.args.get('api-key'), request.args.get('user-id'))
        return app.response_class(
            response=json.dumps(result[1]),
            status=result[0],
            mimetype='application/json'
        )


@bp.route('/listApiKeys', methods=['GET'])
def list_api_keys():
    if request.args.get('api-key') is None:
        return 'key missing'
    else:
        result = list_api_keys_helper(request.args.get('api-key'))
        return app.response_class(
            response=json.dumps(result[1]),
            status=result[0],
            mimetype='application/json'
        )


@bp.route('/setScope', methods=['GET'])
def set_scope():
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
        elif user_db()[actor_id]['role'] != Role.ACTOR:
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

            return app.response_class(
                response=json.dumps({'msg': 'permission modified', 'permission-id': key_to_modify}),
                status=200,
                mimetype='application/json'
            )


def now():
    return datetime.datetime.now(tz=datetime.timezone.utc)


TS_MIN = datetime.datetime(1, 1, 1, 0, 0, 0, 0, tzinfo=datetime.timezone.utc)
TS_MAX = datetime.datetime(9999, 12, 31, 0, 0, 0, 0, tzinfo=datetime.timezone.utc)


def get_actor_state(user_id: str) -> Tuple[int, bool]:
    if user_id not in user_db():
        return 400, False
    elif user_id not in state_db():
        return 200, False
    else:
        if state_db()[user_id]['last_on'] is None:
            return 200, False
        else:
            # print(f"## {state_db()[user_id]['last_on'] - datetime.timedelta(seconds=2)}")
            # print(f"## {now()}")
            # print(f"## {state_db()[user_id]['last_on'] + datetime.timedelta(seconds=user_db()[user_id]['timeout'])}")
            # print(f"\n")
            # print(f"### {state_db()[user_id]['last_on'] - datetime.timedelta(
            #    seconds=2) < now() < state_db()[user_id]['last_on'] + datetime.timedelta(
            #    seconds=user_db()[user_id]['timeout'])}")
            return 200, state_db()[user_id]['last_on'] - datetime.timedelta(
                seconds=2) < now() < state_db()[user_id]['last_on'] + datetime.timedelta(
                seconds=user_db()[user_id]['timeout'])


def sanitize_state_db() -> None:
    for k, v in state_db().items():
        if 'last_on' in v:
            if v['last_on'] is None:
                continue
            elif v['last_on'] - datetime.timedelta(seconds=2) > now():
                state_db()[k]['last_on'] = None


def set_actor_state(user_id: str) -> int:
    if user_id not in user_db():
        return 400
    else:
        if user_id not in state_db():
            state_db()[user_id] = {'last_on': None}
        state_db()[user_id]['last_on'] = now()
        return 200


def log(msg: str):
    print(msg)


def check_valid(user_id: str) -> bool:
    valid_intervals = [(v['from'] if v['from'] is not None else TS_MIN, v['to'] if v['to'] is not None else TS_MAX) for
                       v in valid_db().values() if v['user_id'] == user_id]
    for start, end in valid_intervals:
        if start < now() < end:
            return True
    return False


def get_all_actors(user_id: str, mode: str) -> List[str]:
    if set(mode) not in [set('r'), set('w'), set('rw')]:
        log(f'Invalid mode: {mode}')
        return []
    return [v['actor_id'] for v in permission_db().values() if v['user_id'] == user_id and v['mode'] == mode]


def set_state(actor_id_list: List[str], key: str) -> Tuple[int, dict]:
    if key not in keys_db():
        log(f'key "{key}" not found')
        return 400, {'msg': 'permission denied'}
    else:
        if 'user_id' not in keys_db()[key]:
            log(f'db error: "user_id" not found in keys_db()[{key}]: "{keys_db()[key]}"]')
            return 403, {'msg': 'db error'}
        else:
            user_id = keys_db()[key]['user_id']
            if user_id not in user_db():
                log(f'unknown user id: "user_id" not found in {user_db()=}')
                return 403, {'msg': 'db error'}
            else:
                if 'role' not in user_db()[user_id]:
                    log(f'db error: "type" not in {user_db()[user_id]=}"]')
                    return 403, {'msg': 'db error'}
                else:
                    if user_db()[user_id]['role'] in [Role.USER]:
                        if check_valid(user_id):
                            msg = {}
                            for actor_id in get_all_actors(user_id, 'w'):
                                if actor_id not in actor_id_list:
                                    continue
                                else:
                                    msg[actor_id] = set_actor_state(actor_id)
                            return 200, msg
                    else:
                        log(f'db error: unallowed role: {user_db()[user_id]['role']=}')
                        return 403, {'msg': 'db error'}
