import datetime
import uuid
from typing import List, Tuple, Dict, Union, Optional

from flask import current_app
from sqlalchemy import select, update

from app.extensions import db
from app.models.state import State
from app.models.scope import Scope, Mode
from app.models.user import User, Role
from app.models.valid import Valid
from app.models.usage import Usage, Type
from app.util.util import now, generate_api_key, simple_hash_str, hash_salt_pw_str, check_pw_str

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
    # noinspection PyTypeChecker
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
    # noinspection PyTypeChecker
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


def add_scope(user_id: uuid.UUID, actor_id: uuid.UUID, mode: Mode) -> None:
    scope_data = {'id': uuid.uuid4(), 'user_id': user_id, 'actor_id': actor_id, 'mode': mode.name,
                  'created_at': now(), 'updated_at': now()}
    add_entity_to_db(Scope(**scope_data))


def check_user_if_valid(user_id: uuid.UUID) -> bool:
    valid_rows = get_valid_from_user_id(user_id)
    return eval_ts_list(valid_rows)


def assert_password_properties(password: str):
    assert len(password) >= 8, "password too short"

    from string import ascii_lowercase, ascii_uppercase, digits

    assert any([c in password for c in ascii_lowercase]), 'no lowercase character in password'
    assert any([c in password for c in ascii_uppercase]), 'no uppercase character in password'
    assert any([c in password for c in digits]), 'no numeric character in password'
    assert any([c not in ascii_lowercase + ascii_uppercase + digits for c in password]), \
        'no special character in password'


def set_user_password(user_id: uuid.UUID, password: str) -> None:
    # password assertions
    assert_password_properties(password)
    # get user
    with current_app.app_context():
        db.session.query(User).filter(User.id == user_id).update({'password': hash_salt_pw_str(password),
                                                                  'updated_at': now()})
        db.session.commit()


def check_password(user_id: uuid.UUID, password: str) -> bool:
    with current_app.app_context():
        query = select(User.password).where(User.id == user_id)
        return check_pw_str(password, db.session.execute(query).first()[0])


def set_state(actor_id: uuid.UUID, user_id: uuid.UUID) -> None:
    # check if users valid status
    if not check_user_if_valid(user_id):
        raise PermissionError(f'user currently not valid: {user_id=}')

    # get scope of user
    scopes = get_scopes_from_user_id(user_id)
    if not scopes:
        raise PermissionError(f'no scopes found for user_id "{user_id}"')

    if [s for s in scopes if s[1] == actor_id and s[2] == Mode.write]:
        set_actor_state(actor_id, start=now(), end=now() + datetime.timedelta(seconds=10))
        add_usage(user_id, actor_id, Type.setState)
        return
    else:
        raise PermissionError(f'{actor_id=} scope not found')


def check_scope_valid_return_state(user_id: uuid.UUID, actor_id: uuid.UUID) -> Optional[bool]:
    scopes = [s[1] for s in get_scopes_from_user_id(user_id) if s[1] == actor_id and s[2] == Mode.read]
    if scopes:
        states_list = get_state_from_actor_id(actor_id)
        if eval_ts_list(states_list):
            # state of actor is true
            add_usage(user_id, actor_id, Type.getState_true)
            return True
        else:
            # state of actor is false
            return False
    else:
        return None


def get_state(actor_id: uuid.UUID, user_id: uuid.UUID) -> Optional[bool]:
    if user_id is None:
        raise KeyError(f'user id not found: {user_id}')
    # check if users valid status
    if not check_user_if_valid(user_id):
        raise PermissionError(f'user currently not valid: {user_id=}')

    if check_and_increment():
        sanitize_state_db()

    add_usage(user_id, actor_id, Type.last_getState)

    # get scope of user
    return check_scope_valid_return_state(user_id, actor_id)


def add_usage(user_id: uuid.UUID, actor_id: uuid.UUID, usage_type: Type) -> None:
    usage_data = {'id': uuid.uuid4(), 'user_id': user_id, 'actor_id': actor_id, 'timestamp': now(),
                  'created_at': now(), 'updated_at': now(), 'type': usage_type}

    if usage_type == Type.last_getState:
        with current_app.app_context():
            result = db.session.execute(select(Usage).where(Usage.user_id == actor_id,
                                                            Usage.type == usage_type)).first()
            if result is None:
                add_entity_to_db(Usage(**usage_data))
            else:
                db.session.execute(update(Usage).where(Usage.user_id == actor_id,
                                                       Usage.type == usage_type).values({'timestamp': now()}))
                db.session.commit()
    else:
        add_entity_to_db(Usage(**usage_data))


def add_valid(user_id: uuid.UUID, start: Optional[datetime.datetime] = None,
              end: Optional[datetime.datetime] = None) -> None:
    valid_data = {'id': uuid.uuid4(), 'user_id': user_id, 'start': start, 'end': end,
                  'created_at': now(), 'updated_at': now()}
    add_entity_to_db(Valid(**valid_data))


def add_entity_to_db(entity: Union[User, Valid, Scope, Usage, State]) -> None:
    with current_app.app_context():
        db.session.add(entity)
        db.session.commit()


def check_if_admin_by_api_key(api_key: str) -> bool:
    user_id = get_user_id_from_api_key(api_key)
    if user_id is None:
        return False
    else:
        user_role = get_role_from_user_id(user_id)
        return user_role == Role.admin


def add_bultin_admin_user():
    """ injects the main admin account into the user db if no admin user has been set"""
    with current_app.app_context():
        if not db.session.execute(select(User).filter_by(role=Role.admin, name='_builtin_admin')).scalar_one_or_none():
            response = add_user('_builtin_admin', role=Role.admin)
            admin_api_key = response['api_key']
            print(f'user: "_builtin_admin", api-key: {admin_api_key}')
            db.close_all_sessions()


def add_bultin_maintenance_user():
    """ injects the main admin account into the user db if no admin user has been set"""
    with current_app.app_context():
        if not db.session.execute(
                select(User).filter_by(role=Role.maintenance, name='_builtin_maintenance')).scalar_one_or_none():
            response = add_user('_builtin_maintenance', role=Role.maintenance)
            maintenance_api_key = response['api_key']
            print(f'user: "_builtin_maintenance", api-key: {maintenance_api_key}')
            db.close_all_sessions()


def add_user(name: str, role: Role, email: Optional[str] = None, password: Optional[str] = None) -> Optional[
    Dict[str, str]]:
    if password is not None:
        password = hash_salt_pw_str(password)
    if not isinstance(role, Role):
        raise TypeError(f'unknown role: {role}')
    api_key_raw = generate_api_key()
    user_data = {'id': uuid.uuid4(), 'name': name, 'email': email, 'password': password, 'role': role,
                 'api_key': simple_hash_str(api_key_raw)}
    add_entity_to_db(User(**user_data))
    return {'id': user_data['id'].hex, 'api_key': api_key_raw,
            'password': '-has been set-' if password is not None else None}


def regenerate_api_key(user_id: uuid.UUID) -> Optional[Dict[str, str]]:
    api_key_raw = generate_api_key()
    with current_app.app_context():
        db.session.query(User).filter(User.id == user_id).update(
            {'api_key': simple_hash_str(api_key_raw), 'updated_at': now()})
        db.session.commit()
    return {'api_key': api_key_raw}


def health_check_actor(actor_id: uuid.UUID, timeout: int) -> bool:
    if get_role_from_user_id(actor_id) != Role.actor:
        raise TypeError("not an actor")
    if timeout <= 0:
        raise ValueError("timeout must be larger than 0")
    with current_app.app_context():
        result = db.session.execute(select(Usage.timestamp).filter_by(user_id=actor_id, type=Type.last_getState))
        timedelta_result = sorted([now() - ts[0].replace(tzinfo=datetime.timezone.utc) for ts in result])
        if len(timedelta_result) == 0:
            return False
        else:
            most_recent = timedelta_result[0]
            return most_recent <= datetime.timedelta(seconds=timeout)


def sanitize_state_db() -> None:
    return
    log(f'{now().strftime("%Y-%m-%d %H:%M:%S")} sanitized state table')
    # ToDo: add sanitization logic
    # for k, v in state_db().items():
    #     if 'last_on' in v:
    #         if v['last_on'] is None:
    #             continue
    #         elif v['last_on'] - datetime.timedelta(seconds=2) > now():
    #             state_db()[k]['last_on'] = None


def log(msg: str):
    print(msg)


def set_actor_state(actor_id: uuid.UUID, start: Optional[datetime.datetime],
                    end: Optional[datetime.datetime]) -> None:
    assert (end - start) < datetime.timedelta(minutes=1)
    new_state = State(**{'user_id': actor_id, 'begin': start, 'end': end})
    with current_app.app_context():
        db.session.add(new_state)
        db.session.commit()
