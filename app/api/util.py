import datetime
import os
import uuid
from typing import List, Tuple, Dict, Union, Optional

import flask
from flask import current_app
from sqlalchemy import select

from app.extensions import db
from app.models.state import State
from app.models.scope import Scope, Mode
from app.models.users import Role, Users
from app.util.util import now, simple_hash

QUERY_COUNTER: int = 0
MODULO: int = 100

TS_MIN = datetime.datetime(1, 1, 1, 0, 0, 0, 0, tzinfo=datetime.timezone.utc)
TS_MAX = datetime.datetime(9999, 12, 31, 0, 0, 0, 0, tzinfo=datetime.timezone.utc)


def check_and_increment():
    global QUERY_COUNTER
    if QUERY_COUNTER > 1000 * MODULO:
        QUERY_COUNTER = 0
    else:
        QUERY_COUNTER += 1
    return QUERY_COUNTER % MODULO == 0


def generate_new_key():
    raise NotImplementedError()
    new_key = None
    while new_key is None or new_key in keys_db():
        new_key = str(uuid.uuid4())
    return new_key


def create_user_key(user_id: str):
    raise NotImplementedError()
    if user_id not in user_db():
        log(f'{user_id=} not found in user_db()')
        return 403, {'msg': 'db error'}
    new_key = generate_new_key()
    keys_db()[new_key] = {'user_id': user_id}
    return 200, {'msg': 'key created', 'api-key': new_key}


def get_user_id_from_api_key(api_key: str) -> Optional[uuid.UUID]:
    query = select(Users.id).where(Users.api_key == simple_hash(api_key.encode('utf-8')).hex())
    with current_app.app_context():
        user_ids = [user_id for user_id in db.session.execute(query)]
    if user_ids:
        if len(user_ids) > 1:
            log(f'api key "{simple_hash(api_key.encode('utf-8')).hex()}" found in more than one user row')
        return user_ids[0][0]
    return None


def get_scopes_from_user_id(user_id: uuid.UUID) -> List[Tuple[uuid.UUID, uuid.UUID, Mode]]:
    query = select(Scope.id, Scope.actor_id, Scope.mode).where(Scope.user_id == user_id)
    with current_app.app_context():
        scope_tuples = [tuple(scope_tuple) for scope_tuple in db.session.execute(query)]
    return scope_tuples


def get_state_from_actor_id(actor_id: uuid.UUID) \
        -> List[Tuple[uuid.UUID, datetime.datetime, datetime.datetime]]:
    query = select(State.id, State.begin, State.end).where(State.user_id == actor_id)
    with current_app.app_context():
        state_tuples = [tuple(state_tuple) for state_tuple in db.session.execute(query)]
    return state_tuples


def eval_state(states_list: List[Tuple[uuid.UUID, datetime.datetime, datetime.datetime]]) -> bool:
    ts_now = now()
    for _, start, end in states_list:
        ts_start = start if start is not None else TS_MIN
        ts_start = ts_start.replace(tzinfo=datetime.timezone.utc)
        ts_end = end if end is not None else TS_MAX
        ts_end = ts_end.replace(tzinfo=datetime.timezone.utc)

        if ts_end <= ts_start:
            continue
        elif ts_start <= ts_now <= ts_end:
            return True
        else:
            continue
    return False


def set_state(actor_id_list: List[str], api_key: str) -> Tuple[int, dict]:
    if not isinstance(actor_id_list, list):
        log(f'malformed actors list: {actor_id_list}')
        return 404, {'msg': 'malformed actors list'}

    # get user id from api key
    user_id = get_user_id_from_api_key(api_key)
    if user_id is None:
        log(f'api key not found: {api_key}')
        return 403, {'msg': 'access denied'}
    # get scope of user
    scopes = get_scopes_from_user_id(user_id)
    if not scopes:
        log(f'no scopes found for api_key "{api_key}" and user_id "{user_id}"')
        return 403, {'msg': 'access denied'}
    result = {}
    for actor_id in actor_id_list:
        try:
            uuid.UUID(actor_id)
        except ValueError:
            result[actor_id] = (401, {'msg': 'malformed uuid string'})
            continue

        if [s for s in scopes if s[1] == uuid.UUID(actor_id) and s[2] == Mode.write]:
            set_actor_state(actor_id, start=now(), end=now() + datetime.timedelta(seconds=10))
            result[actor_id] = (200, {'msg': 'success'})
        else:
            log(f'{api_key=}, {actor_id=} scope not found')
            result[actor_id] = (403, {'msg': 'permission denied'})
    return 200, result


def get_state(actor_id_list: List[str], api_key: str) \
        -> Union[Tuple[int, Dict[str, str]], Tuple[int, Dict[str, Tuple[int, Dict[str, bool]]]]]:
    if not isinstance(actor_id_list, list):
        log(f'malformed actors list: {actor_id_list}')
        return 404, {'msg': 'malformed actors list'}

    if check_and_increment():
        sanitize_state_db()
    # get user id from api key
    user_id = get_user_id_from_api_key(api_key)
    if user_id is None:
        log(f'api key not found: {api_key}')
        return 403, {'msg': 'access denied'}
    # get scope of user
    scopes = get_scopes_from_user_id(user_id)

    result = {}
    for actor_id in actor_id_list:
        try:
            uuid.UUID(actor_id)
        except ValueError:
            result[actor_id] = (401, {'msg': 'malformed uuid string'})
            continue

        if [s for s in scopes if s[1] == uuid.UUID(actor_id) and s[2] == Mode.read]:
            a = get_state_from_actor_id(uuid.UUID(actor_id))
            if eval_state(a):
                # state of actor is true
                result[actor_id] = (200, {'state': True})
            else:
                # state of actor is false
                result[actor_id] = (200, {'state': False})
        else:
            log(f'{api_key=}, {actor_id=} scope not found')
            result[actor_id] = (403, {'msg': 'permission denied'})
    return 200, result


def list_api_keys_helper(admin_api_key: str) -> Tuple[int, Dict[str, Union[List[str], str]]]:
    raise NotImplementedError()
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
    raise NotImplementedError()
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
    raise NotImplementedError()
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


# def get_entry_or_none(data: dict, key: str) -> Optional[str]:
#     raise NotImplementedError
#     if key in data.keys():
#         result = data[key]
#         assert isinstance(result, str)
#         if result.strip() == '':
#             return None
#         return result
#     else:
#         return None


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
    log(f'{now().timestamp()} sanitized state table')
    return
    # ToDo: add sanitization logic
    # for k, v in state_db().items():
    #     if 'last_on' in v:
    #         if v['last_on'] is None:
    #             continue
    #         elif v['last_on'] - datetime.timedelta(seconds=2) > now():
    #             state_db()[k]['last_on'] = None


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
    raise NotImplementedError()
    if set(mode) not in [set('r'), set('w'), set('rw')]:
        log(f'Invalid mode: {mode}')
        return []
    return [v['actor_id'] for v in permission_db().values() if v['user_id'] == user_id and v['mode'] == mode]


def set_actor_state(actor_id: str, start: Optional[datetime.datetime],
                    end: Optional[datetime.datetime]) -> None:
    assert (end - start) < datetime.timedelta(minutes=1)
    new_state = State(**{'user_id': uuid.UUID(actor_id), 'begin': start, 'end': end})
    with current_app.app_context():
        db.session.add(new_state)
        db.session.commit()
