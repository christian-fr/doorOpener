import datetime
from enum import Enum
from typing import List, Dict, Optional

from flask import Flask, request
from dotenv import load_dotenv

load_dotenv()

app = Flask(__name__)


class KeyType(Enum):
    NONE = 0
    USER = 1
    ACTOR = 2


USER_DB = {
    '0001': {'actor_ids': ['abcd']},
    '0002': {'actor_ids': ['efgh']},
    '0003': {'actor_ids': ['abcd', 'efgh']},
}

KEY_DB = {
    '052b3945b6913a005c74c52d0a2c48cfc7c10207db775d51950a21bc12dcc472': {
        'type': KeyType.USER,
        'ref_id': '0001',
    },
    '781bd77d28bf4c53e13719136180dcef2d54c75b37b8a3553339859255731d9d': {
        'type': KeyType.USER,
        'ref_id': '0002',
    },
    '8c267d03891a23661ec3e89dbed546297cb86bae05d4767ff01cc0b1616d3499': {
        'type': KeyType.USER,
        'ref_id': '0002',
    },
    '9a9893b036fd1708c518467a203de7405184feff1c2eb315ee8099cd8fedab58': {
        'type': KeyType.ACTOR,
        'ref_id': 'abcd',
    },
    'f160e336939ee5b8ed3206962c488fc5be3f6e35a3ca92fc170e80657958bda3': {
        'type': KeyType.ACTOR,
        'ref_id': 'efgh',
    },
}

ACTOR_DB = {
    'abcd': {'name': 'door street', 'timeout': 5},
    'efgh': {'name': 'door flat', 'timeout': 5},
}

STATE_DB = {
    'abcd': {'last_on': None},
    'efgh': {'last_on': None},
}


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


def get_actor_state(actor_id: str) -> bool:
    if actor_id not in actor_db() or actor_id not in state_db():
        return False
    else:
        if state_db()[actor_id]['last_on'] is None:
            return False
        else:
            return datetime.datetime.now() < state_db()[actor_id]['last_on'] + datetime.timedelta(
                seconds=actor_db()[actor_id]['timeout'])


def set_actor_state(actor_id: str) -> bool:
    if actor_id not in actor_db():
        return False
    else:
        state_db()[actor_id]['last_on'] = datetime.datetime.now()
        return True


def check_key(key: str) -> bool:
    if key not in keys_db():
        return False
    else:
        if 'type' not in keys_db()[key] or 'ref_id' not in keys_db()[key]:
            return False
        else:
            key_type = keys_db()[key]['type']
            ref_id = keys_db()[key]['ref_id']
            if key_type == KeyType.USER:
                if ref_id not in user_db:
                    return False
                else:
                    if 'actor_ids' not in user_db()[ref_id]['actor_ids']:
                        return False
                    else:
                        actor_ids = user_db()[ref_id]['actor_ids']
                        for actor_id in actor_ids:
                            set_actor_state(actor_id)
                        return True
            elif key_type == KeyType.ACTOR:
                if ref_id not in actor_db:
                    return False
                else:
                    get_actor_state(ref_id)
                pass
            else:
                return False


@app.route('/')
def root():
    return 'None'


@app.route('/api/doorOpener', methods=['GET'])
def door_opener():
    if request.args.get('key') is None:
        return 'Key not found'
    else:
        result = check_key(request.args.get('key'))
    return 'Door opened'


if __name__ == '__main__':
    app.run()
