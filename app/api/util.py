import base64
import datetime
import uuid
from typing import List, Tuple, Dict, Union, Optional

from flask import current_app
from sqlalchemy import select

from app.extensions import db
from app.models.state import State
from app.models.scope import Scope, Mode
from app.models.user import User, Role
from app.models.valid import Valid
from app.models.usage import Usage
from app.util.util import now, generate_api_key, simple_hash_str

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


def get_user_id_from_api_key(api_key: str) -> Optional[uuid.UUID]:
    query = select(User.id).where(User.api_key == simple_hash_str(api_key))
    with current_app.app_context():
        user_ids = [user_id for user_id in db.session.execute(query)]
    if user_ids:
        if len(user_ids) > 1:
            log(f'api key "{simple_hash_str(api_key)}" found in more than one user row')
        return user_ids[0][0]
    return None


def get_scopes_from_user_id(user_id: uuid.UUID) -> List[Tuple[uuid.UUID, uuid.UUID, Mode]]:
    query = select(Scope.id, Scope.actor_id, Scope.mode).where(Scope.user_id == user_id)
    with current_app.app_context():
        scope_tuples = [tuple(scope_tuple) for scope_tuple in db.session.execute(query)]
    return scope_tuples


def get_role_from_user_id(user_id: uuid.UUID) -> List[Role]:
    query = select(User.role).where(User.id == user_id)
    with current_app.app_context():
        user_role = [tuple(role_tuple) for role_tuple in db.session.execute(query)][0][0]
    return user_role


def get_state_from_actor_id(actor_id: uuid.UUID) \
        -> List[Tuple[uuid.UUID, datetime.datetime, datetime.datetime]]:
    query = select(State.id, State.begin, State.end).where(State.user_id == actor_id)
    with current_app.app_context():
        state_tuples = [tuple(state_tuple) for state_tuple in db.session.execute(query)]
    return state_tuples


def eval_ts_list(states_list: List[Tuple[uuid.UUID, datetime.datetime, datetime.datetime]]) -> bool:
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


def get_valid_from_user_id(user_id: uuid.UUID) -> List[Tuple[uuid.UUID, datetime.datetime, datetime.datetime]]:
    query = select(Valid.id, Valid.start, Valid.end).where(Valid.user_id == user_id)
    with current_app.app_context():
        valid_rows = [valid_tuple for valid_tuple in db.session.execute(query)]
        return valid_rows


def add_scope(api_key: str, user_id: uuid.UUID, actor_id: uuid.UUID, mode: Mode) -> Tuple[int, dict]:
    admin_user_id = get_user_id_from_api_key(api_key)

    if get_role_from_user_id(admin_user_id) == Role.admin:
        scope_data = {'id': uuid.uuid4(), 'user_id': user_id, 'actor_id': actor_id, 'mode': mode.name,
                      'created_at': now(), 'updated_at': now()}
        with current_app.app_context():
            db.session.add(Scope(**scope_data))
            db.session.commit()
        return 200, {'msg': 'scope created', 'scope_id': scope_data['id'].hex}
    else:
        log(f'user is not an admin: {user_id.hex=}; {api_key=}')
        return 400, {'msg': 'permission denied'}


def check_user_if_valid(user_id: uuid.UUID) -> bool:
    valid_rows = get_valid_from_user_id(user_id)
    return eval_ts_list(valid_rows)


def set_state(actor_id_list: List[str], api_key: str) -> Tuple[int, dict]:
    if not isinstance(actor_id_list, list):
        log(f'malformed actors list: {actor_id_list}')
        return 404, {'msg': 'malformed actors list'}

    # get user id from api key
    user_id = get_user_id_from_api_key(api_key)
    if user_id is None:
        log(f'api key not found: {api_key}')
        return 403, {'msg': 'access denied'}
    # check if users valid status
    if not check_user_if_valid(user_id):
        log(f'user currently not valid: {api_key=}, {user_id=}')
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
    # check if users valid status
    if not check_user_if_valid(user_id):
        log(f'user currently not valid: {api_key=}, {user_id=}')
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
            if eval_ts_list(a):
                # state of actor is true
                result[actor_id] = (200, {'state': True})
                add_usage(actor_id)
            else:
                # state of actor is false
                result[actor_id] = (200, {'state': False})
        else:
            log(f'{api_key=}, {actor_id=} scope not found')
            result[actor_id] = (403, {'msg': 'permission denied'})
    return 200, result


def add_usage(actor_id: str) -> None:
    usage_data = {'id': uuid.uuid4(), 'actor_id': uuid.UUID(actor_id), 'timestamp': now(), 'created_at': now(),
                  'updated_at': now()}
    with current_app.app_context():
        db.session.add(Usage(**usage_data))
        db.session.commit()


def add_valid(api_key: str, user_id: uuid.UUID, start: Optional[datetime.datetime] = None,
              end: Optional[datetime.datetime] = None) -> Tuple[int, dict]:
    admin_id = get_user_id_from_api_key(api_key)

    if get_role_from_user_id(admin_id) != Role.admin:
        log(f'user is not an admin: {admin_id.hex=}; {api_key=}')
        return 400, {'msg': 'permission denied'}
    else:
        valid_data = {'id': uuid.uuid4(), 'user_id': user_id, 'start': start, 'end': end,
                      'created_at': now(),
                      'updated_at': now()}
        with current_app.app_context():
            db.session.add(Valid(**valid_data))
            db.session.commit()
        return 200, {'msg': 'valid created', 'valid_id': valid_data['id'].hex}


def add_user(api_key: str, name: str, role: Role, email: Optional[str] = None, password: Optional[str] = None) \
        -> Tuple[int, dict]:
    user_id = get_user_id_from_api_key(api_key)

    if get_role_from_user_id(user_id) != Role.admin:
        log(f'user is not an admin: {user_id.hex=}; {api_key=}')
        return 400, {'msg': 'permission denied'}
    else:
        api_key_raw = generate_api_key()
        user_data = {'id': uuid.uuid4(), 'name': name, 'email': email, 'password': password, 'role': Role.user,
                     'api_key': simple_hash_str(api_key_raw)}
        with current_app.app_context():
            db.session.add(User(**user_data))
            db.session.commit()
        return 200, {'msg': 'user created', 'user_id': user_data['id'].hex, 'api_key': api_key_raw}


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


def set_actor_state(actor_id: str, start: Optional[datetime.datetime],
                    end: Optional[datetime.datetime]) -> None:
    assert (end - start) < datetime.timedelta(minutes=1)
    new_state = State(**{'user_id': uuid.UUID(actor_id), 'begin': start, 'end': end})
    with current_app.app_context():
        db.session.add(new_state)
        db.session.commit()
