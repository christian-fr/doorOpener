import sys
from typing import Optional

import requests
from app.models.user import Role
from app.models.scope import Mode


def create_user(url: str, api_key: str, user_name: str, role: Role, password: Optional[str]):
    data = {'api-key': api_key, 'name': user_name, 'role': role.name}
    if password is not None:
        data.update({'password': password})
    response = requests.get(url + '/api/addUser', params=data)
    return response.json()


def create_scope(url: str, api_key: str, user_id: str, actor_id: str, mode: Mode):
    data = {'api-key': api_key, 'user-id': user_id, 'actor-id': actor_id, 'mode': mode.name}
    response = requests.get(url + '/api/addScope', params=data)
    return response.json()


def create_valid(url: str, api_key: str, user_id: str):
    data = {'api-key': api_key, 'user-id': user_id}
    response = requests.get(url + '/api/addValid', params=data)
    return response.json()


def get_state(url: str, api_key: str, actor_id: str):
    data = {'api-key': api_key, 'actor-id': actor_id}
    response = requests.get(url + '/api/getState', params=data)
    return response.json()


def set_state(url: str, api_key: str, actor_id: str):
    data = {'api-key': api_key, 'actor-id': actor_id}
    response = requests.post(url + '/api/setState', data=data)
    return response.json()


def main(url: str, admin_api: str, maintenance_api: str):
    actor_data_1 = create_user(url, admin_api, 'actor1', Role.actor, None)
    actor_data_2 = create_user(url, admin_api, 'actor2', Role.actor, None)

    user_data_1 = create_user(url, admin_api, 'user1', Role.user, 'nfr21party')

    scope_data_1 = create_scope(url, admin_api, user_data_1['id'], actor_data_1['id'], Mode.write)
    scope_data_2 = create_scope(url, admin_api, user_data_1['id'], actor_data_2['id'], Mode.write)

    scope_data_3 = create_scope(url, admin_api, actor_data_1['id'], actor_data_1['id'], Mode.read)
    scope_data_4 = create_scope(url, admin_api, actor_data_2['id'], actor_data_2['id'], Mode.read)

    valid_data_1 = create_valid(url, admin_api, user_data_1['id'])
    valid_data_3 = create_valid(url, admin_api, actor_data_1['id'])
    valid_data_4 = create_valid(url, admin_api, actor_data_2['id'])

    get_state_actor1 = get_state(url, actor_data_1['api_key'], actor_data_1['id'])
    set_state_actor1 = set_state(url, user_data_1['api_key'], actor_data_1['id'])
    get_state_actor2 = get_state(url, actor_data_1['api_key'], actor_data_1['id'])

    pass


if __name__ == '__main__':
    url_str = sys.argv[1]
    admin_api_key = sys.argv[2]
    maintenance_api_key = sys.argv[3]
    main(url_str, admin_api_key, maintenance_api_key)
