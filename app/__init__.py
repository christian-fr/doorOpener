import datetime
import json
from enum import Enum
from json import JSONDecodeError
from typing import List, Dict, Tuple

from flask import Flask, request, Config


def now():
    return datetime.datetime.now()


class KeyType(Enum):
    NONE = 0
    USER = 1
    ACTOR = 2
    ADMIN = 3


USER_DB = None
KEY_DB = None
ACTOR_DB = None
STATE_DB = None


def state_db() -> Dict[str, dict]:
    global STATE_DB
    if STATE_DB is None:
        STATE_DB = {}
    return STATE_DB


def actor_db() -> Dict[str, dict]:
    global ACTOR_DB
    if ACTOR_DB is None:
        ACTOR_DB = {}
    return ACTOR_DB


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


def get_actor_state(actor_id: str) -> Tuple[int, bool]:
    if actor_id not in actor_db():
        return 400, False
    elif actor_id not in state_db():
        return 200, False
    else:
        if state_db()[actor_id]['last_on'] is None:
            return 200, False
        else:
            print(f"## {state_db()[actor_id]['last_on'] - datetime.timedelta(seconds=2)}")
            print(f"## {now()}")
            print(f"## {state_db()[actor_id]['last_on'] + datetime.timedelta(seconds=actor_db()[actor_id]['timeout'])}")
            print(f"\n")
            print(f"### {state_db()[actor_id]['last_on'] - datetime.timedelta(
                seconds=2) < now() < state_db()[actor_id]['last_on'] + datetime.timedelta(
                seconds=actor_db()[actor_id]['timeout'])}")
            return 200, state_db()[actor_id]['last_on'] - datetime.timedelta(
                seconds=2) < now() < state_db()[actor_id]['last_on'] + datetime.timedelta(
                seconds=actor_db()[actor_id]['timeout'])


def sanitize_state_db() -> None:
    for k, v in state_db().items():
        if 'last_on' in v:
            if v['last_on'] is None:
                continue
            elif v['last_on'] - datetime.timedelta(seconds=2) > now():
                state_db()[k]['last_on'] = None


def set_actor_state(actor_id: str) -> int:
    if actor_id not in actor_db():
        return 400
    else:
        if actor_id not in state_db():
            state_db()[actor_id] = {'last_on': None}
        state_db()[actor_id]['last_on'] = now()
        return 200


def log(msg: str):
    print(msg)


def set_state(actors: List[str], key: str) -> Tuple[int, dict]:
    if key not in keys_db():
        log(f'key "{key}" not found')
        return 400, {'msg': 'permission denied'}
    else:
        if 'type' not in keys_db()[key]:
            log(f'db error: "type" not found in keys_db()[key]: "{keys_db()[key]}"')
            return 403, {'msg': 'db error'}
        elif 'ref_id' not in keys_db()[key]:
            log(f'db error: "ref_id" not found in keys_db()[key]: "{keys_db()[key]}"')
            return 403, {'msg': 'db error'}
        else:
            key_type = keys_db()[key]['type']
            ref_id = keys_db()[key]['ref_id']
            if key_type != KeyType.USER or ref_id not in user_db():
                return 400, {'msg': 'permission denied'}
            else:
                msg = {}
                for actor_id in actors:
                    msg[actor_id] = set_actor_state(actor_id)
                return 200, msg


COUNTER = 0


def check_and_increment(interval: int = 10, max_val: int = 100000, inc: int = 1):
    global COUNTER
    result = False
    if COUNTER % interval == 0:
        result = True

    COUNTER += 1
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
        if 'type' not in keys_db()[key]:
            log(f'db error: "type" not found in keys_db()[key]: "{keys_db()[key]}"')
            return 403, {'msg': 'db error'}
        elif 'ref_id' not in keys_db()[key]:
            log(f'db error: "ref_id" not found in keys_db()[key]: "{keys_db()[key]}"')
            return 403, {'msg': 'db error'}
        else:
            key_type = keys_db()[key]['type']
            ref_id = keys_db()[key]['ref_id']
            if key_type != KeyType.ACTOR or ref_id not in actor_db():
                return 400, {'msg': 'permission denied'}
            else:
                return 200, {actor_id: get_actor_state(actor_id) for actor_id in actor_id_list}


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
                actors_list = json.loads(request.args.get('actors'))
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
                actors_list = json.loads(request.args.get('actors'))
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


if __name__ == '__main__':
    create_app(config_class=Config).run()
