import datetime
import json
import uuid
from enum import Enum
from json import JSONDecodeError
from typing import List, Dict, Tuple

from flask import Flask, request, Config


def now():
    return datetime.datetime.now(tz=datetime.timezone.utc)


TS_MIN = datetime.datetime(1, 1, 1, 0, 0, 0, 0, tzinfo=datetime.timezone.utc)
TS_MAX = datetime.datetime(9999, 12, 31, 0, 0, 0, 0, tzinfo=datetime.timezone.utc)


class Role(Enum):
    DISABLED = 0
    USER = 0
    ACTOR = 1
    ADMIN = 2


class KeyType(Enum):
    NONE = 0
    USER = 1
    ACTOR = 2
    ADMIN = 3

    def __getitem__(self, item):
        raise NotImplementedError()


USER_DB = None
KEY_DB = None
# ACTOR_DB = None
STATE_DB = None
VALID_DB = None
PERMISSION_DB = None


def permission_db() -> Dict[str, dict]:
    global PERMISSION_DB
    if PERMISSION_DB is None:
        PERMISSION_DB = {}
    return PERMISSION_DB


def valid_db() -> Dict[str, dict]:
    global VALID_DB
    if VALID_DB is None:
        VALID_DB = {}
    return VALID_DB


def state_db() -> Dict[str, dict]:
    global STATE_DB
    if STATE_DB is None:
        STATE_DB = {}
    return STATE_DB


# def actor_db() -> Dict[str, dict]:
#     global ACTOR_DB
#     if ACTOR_DB is None:
#         ACTOR_DB = {}
#     return ACTOR_DB


def keys_db() -> Dict[str, dict]:
    global KEY_DB
    if KEY_DB is None:
        KEY_DB = {}
    return KEY_DB


def user_db() -> Dict[str, dict]:
    global USER_DB
    if USER_DB is None:
        USER_DB = {}
    return USER_DB


def get_actor_state(user_id: str) -> Tuple[int, bool]:
    if user_id not in user_db():
        return 400, False
    elif user_id not in state_db():
        return 200, False
    else:
        if state_db()[user_id]['last_on'] is None:
            return 200, False
        else:
            #print(f"## {state_db()[user_id]['last_on'] - datetime.timedelta(seconds=2)}")
            #print(f"## {now()}")
            #print(f"## {state_db()[user_id]['last_on'] + datetime.timedelta(seconds=user_db()[user_id]['timeout'])}")
            #print(f"\n")
            #print(f"### {state_db()[user_id]['last_on'] - datetime.timedelta(
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
                if not 'role' in user_db()[user_id]:
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


COUNTER = 0


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
    keys_db()[new_key] = {'type': KeyType.USER, 'ref_id': user_id}
    return 200, {'msg': 'key created', 'api-key': new_key}


def create_actor_key(actor_id: str):
    if actor_id not in actor_db():
        log(f'{actor_id=} not found in user_db()')
        return 403, {'msg': 'db error'}
    new_key = generate_new_key()
    keys_db()[new_key] = {'type': KeyType.ACTOR, 'ref_id': actor_id}
    return 200, {'msg': 'key created', 'api-key': new_key}


def create_actor(name: str, actor_id: str = str(uuid.uuid4()), timeout: int = 5):
    assert name.strip() != ''
    if id in actor_db():
        log(f'actor "{name}" already present')
        return 403, {'msg': 'db error'}
    else:
        actor_db()[actor_id] = {'name': name, 'timeout': timeout}
        return 200, {'msg': 'actor created', 'actor-id': actor_id}


def create_user(name: str, user_id: str = str(uuid.uuid4()), actor_ids: List[str] = None,
                valid_from: datetime.datetime = None,
                valid_until: datetime.datetime = None):
    if actor_ids is None:
        actor_ids = []
    assert user_id.strip() != ''
    if user_id in user_db():
        log(f'user id "{user_id}" already present')
        return 403, {'msg': 'db error'}
    else:
        user_db()[user_id] = {'name': name, 'actor_ids': actor_ids, 'valid_from': valid_from,
                              'valid_until': valid_until}
        return 200, {'msg': 'user created', 'user-id': user_id}


def check_and_increment(interval: int = 10, max_val: int = 100000, inc: int = 1):
    global COUNTER
    result = False
    if COUNTER % interval == 0:
        result = True

    COUNTER += inc
    if COUNTER > max_val:
        COUNTER = 0

    return result


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

            if not 'role' in user_db()[user_id]:
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
                        log(f'permission error: user not valid: {user_id} // {[v for v in valid_db().values() if v["user_id"] == user_id]}')
                        return 403, {'msg': 'permission error'}

                else:
                    log(f'db error: unallowed role: {user_db()[user_id]['role']=}')
                    return 403, {'msg': 'db error'}


def create_app(config_class=Config):
    app = Flask(__name__)
    app.config.from_object(config_class)

    # # Register blueprints here
    # from app.main import bp as main_bp
    # app.register_blueprint(main_bp)

    # with app.app_context():
    #     db.create_all()

    @app.route('/')
    def root():
        return 'None'

    @app.route('/api/setDoorState', methods=['GET'])
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

    @app.route('/api/getDoorState', methods=['GET'])
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

    @app.route('/api/createUser', methods=['GET'])
    def create_user():
        raise NotImplementedError()
        if request.args.get('actors') is None:
            return 'Actor ID not found'
        elif request.args.get('key') is None:
            return 'Key not found'
        else:
            result = set_state(request.args.get('actors'), request.args.get('key'))
        return 'Door opened'

    return app

    @app.route('/api/createActor', methods=['GET'])
    def create_actor():
        raise NotImplementedError()
        if request.args.get('actors') is None:
            return 'Actor ID not found'
        elif request.args.get('key') is None:
            return 'Key not found'
        else:
            result = set_state(request.args.get('actors'), request.args.get('key'))
        return 'Door opened'

    return app


if __name__ == '__main__':
    create_app(config_class=Config).run()
