import datetime
import uuid
from unittest import TestCase

import flask
from sqlalchemy import select

from app.app import create_app, db, User, Valid, State
from app.api.func import get_state, set_state, add_user, add_scope, add_valid, assert_password_properties, \
    set_user_password, check_password, add_usage, health_check_actor, regenerate_api_key
from app.models.scope import Mode, Scope
from app.models.usage import Type
from app.models.user import Role
from app.util.util import simple_hash_str, hash_salt_pw_str, generate_api_key, check_pw, check_pw_str
from tests.context.testfixture_config import Config

from tests.util.mock_datetime import mock_datetime_now

TS_11_00_00 = datetime.datetime(year=2024, month=2, day=20, hour=11, minute=0, second=0, tzinfo=datetime.timezone.utc)
TS_12_29_00 = datetime.datetime(year=2024, month=2, day=20, hour=12, minute=29, second=0, tzinfo=datetime.timezone.utc)
TS_12_30_00 = datetime.datetime(year=2024, month=2, day=20, hour=12, minute=30, second=0, tzinfo=datetime.timezone.utc)
TS_12_30_01 = datetime.datetime(year=2024, month=2, day=20, hour=12, minute=30, second=1, tzinfo=datetime.timezone.utc)
TS_12_30_02 = datetime.datetime(year=2024, month=2, day=20, hour=12, minute=30, second=2, tzinfo=datetime.timezone.utc)
TS_12_30_03 = datetime.datetime(year=2024, month=2, day=20, hour=12, minute=30, second=3, tzinfo=datetime.timezone.utc)
TS_12_30_04 = datetime.datetime(year=2024, month=2, day=20, hour=12, minute=30, second=4, tzinfo=datetime.timezone.utc)
TS_12_30_05 = datetime.datetime(year=2024, month=2, day=20, hour=12, minute=30, second=5, tzinfo=datetime.timezone.utc)
TS_12_30_06 = datetime.datetime(year=2024, month=2, day=20, hour=12, minute=30, second=6, tzinfo=datetime.timezone.utc)
TS_12_30_07 = datetime.datetime(year=2024, month=2, day=20, hour=12, minute=30, second=7, tzinfo=datetime.timezone.utc)
TS_12_30_08 = datetime.datetime(year=2024, month=2, day=20, hour=12, minute=30, second=8, tzinfo=datetime.timezone.utc)
TS_12_30_09 = datetime.datetime(year=2024, month=2, day=20, hour=12, minute=30, second=9, tzinfo=datetime.timezone.utc)
TS_12_30_10 = datetime.datetime(year=2024, month=2, day=20, hour=12, minute=30, second=10, tzinfo=datetime.timezone.utc)
TS_12_30_11 = datetime.datetime(year=2024, month=2, day=20, hour=12, minute=30, second=11, tzinfo=datetime.timezone.utc)
TS_12_30_12 = datetime.datetime(year=2024, month=2, day=20, hour=12, minute=30, second=12, tzinfo=datetime.timezone.utc)
TS_12_31_00 = datetime.datetime(year=2024, month=2, day=20, hour=12, minute=31, second=0, tzinfo=datetime.timezone.utc)
TS_16_00_00 = datetime.datetime(year=2024, month=2, day=20, hour=16, minute=0, second=0, tzinfo=datetime.timezone.utc)

ACTOR0001_USER_ID = uuid.UUID('1dad0dc3-f862-4b41-9608-2ee1fa3050c2')
ACTOR0001_KEY = '9a9893b036fd1708c518467a203de7405184feff1c2eb315ee8099cd8fedab58'
ACTOR0001_KEY_HASH = simple_hash_str(ACTOR0001_KEY)

ACTOR0002_USER_ID = uuid.UUID('d526569c-4743-4d3e-a742-128051f63f72')
ACTOR0002_KEY = 'f160e336939ee5b8ed3206962c488fc5be3f6e35a3ca92fc170e80657958bda3'
ACTOR0002_KEY_HASH = simple_hash_str(ACTOR0002_KEY)

ACTOR0003_USER_ID = uuid.UUID('df809f8d-7689-439c-8dc8-d73d1d49e562')
ACTOR0003_KEY = 'dc684777eb8a2edea57cbf7ca85c3799d6064e0ee6c307a24f182fa32cebd697'
ACTOR0003_KEY_HASH = simple_hash_str(ACTOR0003_KEY)

USER0001_USER_ID = uuid.UUID('1f4a6f9c-af4a-4a32-976d-e86a1487ec43')
USER0001_KEY = '052b3945b6913a005c74c52d0a2c48cfc7c10207db775d51950a21bc12dcc472'
USER0001_KEY_HASH = simple_hash_str(USER0001_KEY)
USER0001_PASSWORD = 'SonneMondUndSterne'
USER0001_PW_HASH = hash_salt_pw_str(USER0001_PASSWORD)

USER0002_USER_ID = uuid.UUID('72031898-24eb-46d4-b4de-40355517ef8e')
USER0002_KEY = '781bd77d28bf4c53e13719136180dcef2d54c75b37b8a3553339859255731d9d'
USER0002_KEY_HASH = simple_hash_str(USER0002_KEY)
USER0002_PASSWORD = 'OneAndOneAndOneIsThree'
USER0002_PW_HASH = hash_salt_pw_str(USER0002_PASSWORD)

USER0003_USER_ID = uuid.UUID('d8977529-31bd-4f3e-b24c-91f31d962487')
USER0003_KEY = '8c267d03891a23661ec3e89dbed546297cb86bae05d4767ff01cc0b1616d3499'
USER0003_KEY_HASH = simple_hash_str(USER0003_KEY)
USER0003_PASSWORD = 'RocknRoll'
USER0003_PW_HASH = hash_salt_pw_str(USER0003_PASSWORD)

USER0004_USER_ID = uuid.UUID('c100c404-4f65-4a23-b5d9-0979dad67fec')
USER0004_KEY = '58a0d55f80247f4b554dcae9ad274b8e96105519cd87a344bb017f42cc762b86'
USER0004_KEY_HASH = simple_hash_str(USER0004_KEY)
USER0004_PASSWORD = 'AlleMeineEntchen'
USER0004_PW_HASH = hash_salt_pw_str(USER0004_PASSWORD)

USER0005_USER_ID = uuid.UUID('17b6909f-565f-4416-a587-3a8791aef0e7')
USER0005_KEY = '961e67183206708d327ae766e6ac34f6ac0c082e0af8763ca8e8d3228496259a'
USER0005_KEY_HASH = simple_hash_str(USER0005_KEY)
USER0005_PASSWORD = 'JingleBellsRock'
USER0005_PW_HASH = hash_salt_pw_str(USER0005_PASSWORD)

USER0006_USER_ID = uuid.UUID('9f1b6399-f051-44c3-bab3-1a4b8eb81e28')
USER0006_KEY = '535b4e070c23cca91a2044258b2f8cbabe7c58c5fe18f7a88d13c85a3c8db068'
USER0006_KEY_HASH = simple_hash_str(USER0006_KEY)
USER0006_PASSWORD = 'SuesserDieGlockenNieKlingen'
USER0006_PW_HASH = hash_salt_pw_str(USER0006_PASSWORD)

DISABLED_USER_ID = uuid.UUID('4c86f252-7d14-4776-a9a7-2e85e23b4f69')
DISABLED_KEY = '9c1e953d91c1bf590dcb2a6011d8f0370fd0df12baea0adfd536175596f10d43'
DISABLED_KEY_HASH = simple_hash_str(DISABLED_KEY)
DISABLED_PASSWORD = 'KeinSchoenerLand'
DISABLED_PW_HASH = hash_salt_pw_str(DISABLED_PASSWORD)

MAINTENANCE_USER_ID = uuid.UUID('e96886c4-c840-4277-9bd7-b0676fb88fdd')
MAINTENANCE_KEY = '7e1c9a245c013097842472199176ee3f951b47ea6d7d3ce45a68ec01efeeb728'
MAINTENANCE_KEY_HASH = simple_hash_str(MAINTENANCE_KEY)
MAINTENANCE_PASSWORD = 'DiesUndDas'
MAINTENANCE_PW_HASH = hash_salt_pw_str(MAINTENANCE_PASSWORD)

BUILTIN_ADMIN_USER_ID = None
BUILTIN_ADMIN_KEY = None
BUILTIN_ADMIN_KEY_HASH = None

ADMIN_USER_ID = uuid.UUID('32546de6-7c94-41b8-812b-4f5786b71e1c')
ADMIN_KEY = '98cfefb9d2c1477b3d98ebd19ec7a69bc0f82ce81a1ee88fcbdfe07a7681a829'
ADMIN_KEY_HASH = simple_hash_str(ADMIN_KEY)
ADMIN_PASSWORD = 'SuperSudo'
ADMIN_PW_HASH = hash_salt_pw_str(ADMIN_PASSWORD)

for key, hash_str in [(USER0001_KEY, USER0001_KEY_HASH),
                      (USER0002_KEY, USER0002_KEY_HASH),
                      (USER0003_KEY, USER0003_KEY_HASH),
                      (USER0004_KEY, USER0004_KEY_HASH),
                      (USER0005_KEY, USER0005_KEY_HASH),
                      (USER0006_KEY, USER0006_KEY_HASH),
                      (DISABLED_KEY, DISABLED_KEY_HASH),
                      (ADMIN_KEY, ADMIN_KEY_HASH),
                      (MAINTENANCE_KEY, MAINTENANCE_KEY_HASH)]:
    assert simple_hash_str(key) == hash_str

VALID01_ID = uuid.UUID('c5026b88-7782-4dc3-b930-3c8121da7644')
VALID02_ID = uuid.UUID('5a15b116-6f48-4186-9c5b-b8240d5a8ff3')
VALID03_ID = uuid.UUID('02ed3c6b-a9aa-4207-8f42-c3ec57359322')
VALID04_ID = uuid.UUID('d04e218a-64b0-432c-aaf7-e4dfac8b635a')
VALID05_ID = uuid.UUID('3f68de07-f81f-4b10-a28d-2c235d1d72de')
VALID06_ID = uuid.UUID('0c59b73c-bd39-48bd-9d75-48d559202cde')
VALID07_ID = uuid.UUID('7cf580c4-22a1-4b9e-b3c1-08bc3421f18e')
VALID08_ID = uuid.UUID('5ef12355-55e4-4eb9-849d-92d3a3e1a2ef')
VALID09_ID = uuid.UUID('37d6f246-f575-43b4-b0c5-5525ef02b0f6')
VALID10_ID = uuid.UUID('b6d8f316-3872-4dc1-ad30-1ba7ce86ace3')

SCOPE01_ID = uuid.UUID('6af8022f-3843-4f6d-aedf-82054bef1425')
SCOPE02_ID = uuid.UUID('ad178135-5de5-4e8f-8c02-662a831f5ab2')
SCOPE03_ID = uuid.UUID('dbb5aa11-6898-4b0e-bf7a-71beeba86e4f')
SCOPE04_ID = uuid.UUID('bd7cca24-8658-4724-abc9-481355a5442e')
SCOPE05_ID = uuid.UUID('e1f760d0-23d0-4d31-aa08-c72b3e550a80')
SCOPE06_ID = uuid.UUID('3df49528-24c2-4397-b346-65e56e7e1f34')
SCOPE07_ID = uuid.UUID('bc276ca1-f019-4688-8b62-90643cc5bc95')

STATE01_ID = uuid.UUID('57441403-e8f3-438c-999d-6264079eb95a')
STATE02_ID = uuid.UUID('1b785226-a486-4e1b-b2c9-512d7babdc38')
STATE03_ID = uuid.UUID('9ab29552-913f-40c3-8f1d-fd0fac434b52')
STATE04_ID = uuid.UUID('3152c612-82aa-4f88-a927-6ded02cd7163')


def date_to_str(date: datetime.datetime) -> str:
    return date.strftime('%Y-%m-%dT%H:%M:%S.%f')


def str_to_date(date: str) -> datetime.datetime:
    return datetime.datetime.strptime(date, '%Y-%m-%dT%H:%M:%S.%f')


TS_12_29_00str = date_to_str(TS_12_29_00)
TS_12_30_06str = date_to_str(TS_12_30_06)


def set_up_users(app: flask.app.Flask, timestamp: datetime.datetime) -> None:
    with mock_datetime_now(timestamp, datetime):
        user0001_data = {'id': USER0001_USER_ID, 'name': 'USER0001', 'email': None,
                         'password': USER0001_PW_HASH, 'api_key': USER0001_KEY_HASH, 'role': Role.user, }
        user0002_data = {'id': USER0002_USER_ID, 'name': 'USER0002', 'email': None,
                         'password': USER0002_PW_HASH, 'api_key': USER0002_KEY_HASH, 'role': Role.user, }
        user0003_data = {'id': USER0003_USER_ID, 'name': 'USER0003', 'email': None,
                         'password': USER0003_PW_HASH, 'api_key': USER0003_KEY_HASH, 'role': Role.user, }
        user0004_data = {'id': USER0004_USER_ID, 'name': 'USER0004', 'email': None,
                         'password': USER0004_PW_HASH, 'api_key': USER0004_KEY_HASH, 'role': Role.user, }
        user0005_data = {'id': USER0005_USER_ID, 'name': 'USER0005', 'email': None,
                         'password': USER0005_PW_HASH, 'api_key': USER0005_KEY_HASH, 'role': Role.user, }
        user0006_data = {'id': USER0006_USER_ID, 'name': 'USER0006', 'email': None,
                         'password': USER0006_PW_HASH, 'api_key': USER0006_KEY_HASH, 'role': Role.user, }
        actor0001_data = {'id': ACTOR0001_USER_ID, 'name': 'ACTOR1', 'email': None,
                          'password': None, 'api_key': ACTOR0001_KEY_HASH, 'role': Role.actor, }
        actor0002_data = {'id': ACTOR0002_USER_ID, 'name': 'ACTOR2', 'email': None,
                          'password': None, 'api_key': ACTOR0002_KEY_HASH, 'role': Role.actor, }
        actor0003_data = {'id': ACTOR0003_USER_ID, 'name': 'ACTOR3', 'email': None,
                          'password': None, 'api_key': ACTOR0003_KEY_HASH, 'role': Role.actor, }
        disabled_data = {'id': DISABLED_USER_ID, 'name': 'DISABLED0001', 'email': None,
                         'password': DISABLED_PW_HASH, 'api_key': DISABLED_KEY_HASH, 'role': Role.deactivated, }
        maintenance_data = {'id': MAINTENANCE_USER_ID, 'name': 'MAINTENANCE0001', 'email': None,
                            'password': MAINTENANCE_PW_HASH, 'api_key': MAINTENANCE_KEY_HASH,
                            'role': Role.maintenance, }
        admin_data = {'id': ADMIN_USER_ID, 'name': 'ADMIN', 'email': None,
                      'password': ADMIN_PW_HASH, 'api_key': ADMIN_KEY_HASH, 'role': Role.admin, }

        data_list = [user0001_data, user0002_data, user0003_data, user0004_data, user0005_data, user0006_data,
                     actor0001_data, actor0002_data, actor0003_data, disabled_data, admin_data, maintenance_data]
        created_updated_dict = {'created_at': datetime.datetime.now(), 'updated_at': datetime.datetime.now()}

        user_list = [User(**data, **created_updated_dict) for data in data_list]
        with app.app_context():
            for user in user_list:
                db.session.add(user)
                db.session.commit()


def set_up_valid(app: flask.app.Flask, timestamp: datetime.datetime) -> None:
    with mock_datetime_now(timestamp, datetime):
        valid01_data = {'id': VALID01_ID, 'user_id': USER0001_USER_ID, 'start': None, 'end': None}
        valid02_data = {'id': VALID02_ID, 'user_id': USER0002_USER_ID, 'start': None, 'end': None}
        valid03_data = {'id': VALID03_ID, 'user_id': USER0003_USER_ID, 'start': None, 'end': None}
        valid04_data = {'id': VALID04_ID, 'user_id': USER0004_USER_ID, 'start': None,
                        'end': TS_12_29_00}
        valid05_data = {'id': VALID05_ID, 'user_id': USER0005_USER_ID, 'start': TS_12_29_00,
                        'end': TS_12_30_06}
        valid06_data = {'id': VALID06_ID, 'user_id': USER0006_USER_ID, 'start': TS_12_30_06,
                        'end': TS_12_29_00}
        valid07_data = {'id': VALID07_ID, 'user_id': ACTOR0001_USER_ID, 'start': None,
                        'end': None}
        valid08_data = {'id': VALID08_ID, 'user_id': ACTOR0002_USER_ID, 'start': None,
                        'end': None}
        valid09_data = {'id': VALID09_ID, 'user_id': ACTOR0003_USER_ID, 'start': None,
                        'end': TS_12_30_11}
        valid10_data = {'id': VALID10_ID, 'user_id': USER0004_USER_ID, 'start': None,
                        'end': TS_12_30_11}

        created_updated_dict = {'created_at': datetime.datetime.now(), 'updated_at': datetime.datetime.now()}

        valid_data_list = [valid01_data, valid02_data, valid03_data, valid04_data, valid05_data, valid06_data,
                           valid07_data, valid08_data, valid09_data, valid10_data]
        valid_list = [Valid(**data, **created_updated_dict) for data in valid_data_list]
        with app.app_context():
            for valid in valid_list:
                db.session.add(valid)
                db.session.commit()


def set_up_scope(app: flask.app.Flask, timestamp: datetime.datetime) -> None:
    with mock_datetime_now(timestamp, datetime):
        scope01_data = {'id': SCOPE01_ID, 'user_id': ACTOR0001_USER_ID,
                        'actor_id': ACTOR0001_USER_ID, 'mode': Mode.read}
        scope02_data = {'id': SCOPE02_ID, 'user_id': ACTOR0002_USER_ID,
                        'actor_id': ACTOR0002_USER_ID, 'mode': Mode.read}
        scope03_data = {'id': SCOPE03_ID, 'user_id': USER0001_USER_ID,
                        'actor_id': ACTOR0001_USER_ID, 'mode': Mode.write}
        scope04_data = {'id': SCOPE04_ID, 'user_id': USER0002_USER_ID,
                        'actor_id': ACTOR0002_USER_ID, 'mode': Mode.write}
        scope05_data = {'id': SCOPE05_ID, 'user_id': USER0003_USER_ID,
                        'actor_id': ACTOR0001_USER_ID, 'mode': Mode.write}
        scope06_data = {'id': SCOPE06_ID, 'user_id': USER0003_USER_ID,
                        'actor_id': ACTOR0002_USER_ID, 'mode': Mode.write}
        scope07_data = {'id': SCOPE07_ID, 'user_id': ACTOR0003_USER_ID,
                        'actor_id': ACTOR0003_USER_ID, 'mode': Mode.read}

        created_updated_dict = {'created_at': datetime.datetime.now(), 'updated_at': datetime.datetime.now()}

        scope_data_list = [scope01_data, scope02_data, scope03_data, scope04_data, scope05_data, scope06_data,
                           scope07_data]

        scope_list = [Scope(**data, **created_updated_dict) for data in scope_data_list]
        with app.app_context():
            for valid in scope_list:
                db.session.add(valid)
                db.session.commit()


def set_up_state(app: flask.app.Flask, timestamp: datetime.datetime) -> None:
    with mock_datetime_now(timestamp, datetime):
        state01_data = {'id': STATE01_ID, 'user_id': ACTOR0001_USER_ID, 'begin': TS_12_30_03,
                        'end': TS_12_30_10}
        state02_data = {'id': STATE02_ID, 'user_id': ACTOR0002_USER_ID, 'begin': TS_11_00_00,
                        'end': TS_12_29_00}
        state03_data = {'id': STATE03_ID, 'user_id': ACTOR0001_USER_ID, 'begin': None,
                        'end': TS_12_30_01}
        state04_data = {'id': STATE04_ID, 'user_id': ACTOR0002_USER_ID, 'begin': TS_12_30_04,
                        'end': None}

        created_updated_dict = {'created_at': datetime.datetime.now(), 'updated_at': datetime.datetime.now()}

        state_data_list = [state01_data, state02_data, state03_data, state04_data]

        state_list = [State(**data, **created_updated_dict) for data in state_data_list]
        with app.app_context():
            for valid in state_list:
                db.session.add(valid)
                db.session.commit()


class TestApiFunctions(TestCase):
    def setUp(self):
        self.app = create_app(config_class=Config.get_cls())
        self.app_test = self.app.test_client()

        with self.app.app_context():
            # set api_key for _builtin_admin
            global BUILTIN_ADMIN_KEY
            BUILTIN_ADMIN_KEY = generate_api_key()
            User.query.filter_by(name='_builtin_admin').update({'api_key': simple_hash_str(BUILTIN_ADMIN_KEY)})
            db.session.commit()

        set_up_users(self.app, TS_11_00_00)
        set_up_valid(self.app, TS_11_00_00)
        set_up_scope(self.app, TS_11_00_00)

    def tearDown(self):
        with self.app.app_context():
            db.session.close()
            db.engine.dispose()
        Config.TEMP_DIR.cleanup()

    def test_set_state(self):
        with self.app.app_context():
            for ts in [TS_12_29_00, TS_12_30_00, TS_12_30_01, TS_12_30_02, TS_12_30_02, TS_12_30_03, TS_12_30_04,
                       TS_12_30_05, TS_12_30_06, TS_12_30_07, TS_12_30_08, TS_12_30_09, TS_12_30_10, TS_12_30_11,
                       TS_12_30_12]:
                with mock_datetime_now(ts, datetime):
                    self.assertFalse(get_state(ACTOR0002_USER_ID, ACTOR0002_USER_ID))
            with mock_datetime_now(TS_12_30_01, datetime):
                set_state(ACTOR0002_USER_ID, USER0002_USER_ID)

            for ts in [TS_12_29_00, TS_12_30_00, TS_12_30_12]:
                with mock_datetime_now(ts, datetime):
                    self.assertFalse(False, get_state(ACTOR0002_USER_ID, ACTOR0002_USER_ID))
            for ts in [TS_12_30_01, TS_12_30_02, TS_12_30_02, TS_12_30_03, TS_12_30_04, TS_12_30_05, TS_12_30_06,
                       TS_12_30_07, TS_12_30_08, TS_12_30_09, TS_12_30_10, TS_12_30_11, ]:
                with mock_datetime_now(ts, datetime):
                    self.assertTrue(get_state(ACTOR0002_USER_ID, ACTOR0002_USER_ID))

    def test_get_state(self):
        # initially set up state table
        set_up_state(self.app, TS_11_00_00)

        with self.app.app_context():
            for ts in [TS_12_30_02, TS_12_30_11, TS_12_30_12]:
                with mock_datetime_now(ts, datetime):
                    self.assertIsNone(get_state(ACTOR0001_USER_ID, ACTOR0002_USER_ID))
            for ts in [TS_12_30_01, TS_12_30_03, TS_12_30_04, TS_12_30_05, TS_12_30_06, TS_12_30_07, TS_12_30_08,
                       TS_12_30_09, TS_12_30_10]:
                with mock_datetime_now(ts, datetime):
                    self.assertTrue(get_state(ACTOR0001_USER_ID, ACTOR0001_USER_ID))

            # more than one actor in list
            for ts in [TS_12_29_00, TS_12_30_04]:
                with mock_datetime_now(ts, datetime):
                    self.assertTrue(get_state(ACTOR0001_USER_ID, ACTOR0001_USER_ID))
                    self.assertIsNone(get_state(ACTOR0002_USER_ID, ACTOR0001_USER_ID))
                    self.assertIsNone(get_state(ACTOR0001_USER_ID, ACTOR0002_USER_ID))
                    self.assertTrue(get_state(ACTOR0002_USER_ID, ACTOR0002_USER_ID))

                with mock_datetime_now(TS_12_30_02, datetime):
                    self.assertFalse(get_state(ACTOR0001_USER_ID, ACTOR0001_USER_ID))
                    self.assertIsNone(get_state(ACTOR0002_USER_ID, ACTOR0001_USER_ID))
                    self.assertIsNone(get_state(ACTOR0001_USER_ID, ACTOR0002_USER_ID))
                    self.assertFalse(get_state(ACTOR0002_USER_ID, ACTOR0002_USER_ID))

                with mock_datetime_now(TS_12_30_11, datetime):
                    self.assertFalse(get_state(ACTOR0001_USER_ID, ACTOR0001_USER_ID))
                    self.assertIsNone(get_state(ACTOR0002_USER_ID, ACTOR0001_USER_ID))
                    self.assertIsNone(get_state(ACTOR0001_USER_ID, ACTOR0002_USER_ID))
                    self.assertTrue(get_state(ACTOR0002_USER_ID, ACTOR0002_USER_ID))

                with mock_datetime_now(TS_12_30_11, datetime):
                    # get state for a wrong actor id
                    unknown_id = uuid.uuid4()
                    self.assertIsNone(get_state(unknown_id, ACTOR0001_USER_ID))

                    # get state for an actor with no entries in state table
                    self.assertFalse(get_state(ACTOR0003_USER_ID, ACTOR0003_USER_ID))

                    # get initial state for an existing actor id, but with a key that is lacking permission
                    self.assertIsNone(get_state(ACTOR0001_USER_ID, ACTOR0003_USER_ID))

                # get state with actor id that is currently valid
                with mock_datetime_now(TS_12_30_11, datetime):
                    self.assertFalse(get_state(ACTOR0003_USER_ID, ACTOR0003_USER_ID))
                # get state with actor id that is currently invalid
                with mock_datetime_now(TS_12_30_12, datetime):
                    with self.assertRaises(PermissionError):
                        get_state(ACTOR0003_USER_ID, ACTOR0003_USER_ID)

                with mock_datetime_now(TS_12_30_11, datetime):
                    # this is an unknown key
                    unknown_id = uuid.uuid4()
                    with self.assertRaises(PermissionError):
                        get_state(ACTOR0001_USER_ID, unknown_id)

    def test_add_user(self):
        with (self.app.app_context()):
            properties = [User.id, User.api_key, User.name, User.role]
            query = select(*properties)
            user_data_ex_ante = {user_data[0]: user_data[1:] for user_data in db.session.execute(query)}

            result_json = add_user('new User', Role.user)
            user_id = result_json['id']
            user_api_key = result_json['api_key']
            user_password = result_json['password']
            self.assertTrue(isinstance(uuid.UUID(user_id), uuid.UUID), uuid.UUID)
            self.assertEqual(len(generate_api_key()), len(user_api_key))
            self.assertIsNone(user_password)

            query = select(*properties)
            user_data_ex_post = {user_data[0]: user_data[1:] for user_data in db.session.execute(query)}
            new_user_key = set(user_data_ex_post.keys()).difference(user_data_ex_ante)
            assert len(new_user_key) == 1
            new_user_data = user_data_ex_post[list(new_user_key)[0]]
            self.assertEqual(len(simple_hash_str(generate_api_key())), len(new_user_data[0]))
            self.assertEqual('new User', new_user_data[1])
            self.assertEqual(Role.user, new_user_data[2])

    def test_add_user_error(self):
        with (self.app.app_context()):
            properties = [User.id, User.api_key, User.name, User.role]
            query = select(*properties)
            user_data_ex_ante = {user_data[0]: user_data[1:] for user_data in db.session.execute(query)}
            with self.assertRaises(TypeError):
                # noinspection PyTypeChecker
                add_user('new User', None)

            query = select(*properties)
            user_data_ex_post = {user_data[0]: user_data[1:] for user_data in db.session.execute(query)}
            self.assertEqual(user_data_ex_ante, user_data_ex_post)

    def test_add_valid01(self):
        with (self.app.app_context()):
            properties = [Valid.id, Valid.user_id, Valid.start, Valid.end]
            query = select(*properties)
            valid_data_ex_ante = {valid_data[0]: valid_data[1:] for valid_data in db.session.execute(query)}

            add_valid(USER0003_USER_ID, TS_12_30_02, TS_12_30_06)

            query = select(*properties)
            valid_data_ex_post = {valid_data[0]: valid_data[1:] for valid_data in db.session.execute(query)}
            new_user_key = set(valid_data_ex_post.keys()).difference(valid_data_ex_ante)
            assert len(new_user_key) == 1
            new_valid_data = valid_data_ex_post[list(new_user_key)[0]]
            self.assertTrue(isinstance(new_valid_data[0], uuid.UUID))
            self.assertEqual(TS_12_30_02, new_valid_data[1].replace(tzinfo=datetime.timezone.utc))
            self.assertEqual(TS_12_30_06, new_valid_data[2].replace(tzinfo=datetime.timezone.utc))

    def test_add_valid02(self):
        with (self.app.app_context()):
            properties = [Valid.id, Valid.user_id, Valid.start, Valid.end]
            query = select(*properties)
            valid_data_ex_ante = {valid_data[0]: valid_data[1:] for valid_data in db.session.execute(query)}

            add_valid(USER0003_USER_ID, TS_12_30_02, None)

            query = select(*properties)
            valid_data_ex_post = {valid_data[0]: valid_data[1:] for valid_data in db.session.execute(query)}
            new_user_key = set(valid_data_ex_post.keys()).difference(valid_data_ex_ante)
            assert len(new_user_key) == 1
            new_valid_data = valid_data_ex_post[list(new_user_key)[0]]
            self.assertTrue(isinstance(new_valid_data[0], uuid.UUID))
            self.assertEqual(TS_12_30_02, new_valid_data[1].replace(tzinfo=datetime.timezone.utc))
            self.assertIsNone(new_valid_data[2])

    def test_add_scope(self):
        with (self.app.app_context()):
            properties = [Scope.id, Scope.user_id, Scope.actor_id, Scope.mode]
            query = select(*properties)
            scope_data_ex_ante = {scope_data[0]: scope_data[1:] for scope_data in db.session.execute(query)}
            add_scope(USER0006_USER_ID, ACTOR0003_USER_ID, Mode.unset)

            query = select(*properties)
            scope_data_ex_post = {scope_data[0]: scope_data[1:] for scope_data in db.session.execute(query)}
            new_scope_key = set(scope_data_ex_post.keys()).difference(scope_data_ex_ante)
            assert len(new_scope_key) == 1
            new_scope_data = scope_data_ex_post[list(new_scope_key)[0]]

            self.assertEqual(USER0006_USER_ID, new_scope_data[0])
            self.assertEqual(ACTOR0003_USER_ID, new_scope_data[1])
            self.assertEqual(Mode.unset, new_scope_data[2])

    def test_assert_password(self):
        with self.assertRaises(AssertionError) as err:
            assert_password_properties("123abC")
        exc = err.exception
        self.assertEqual(exc.args, ('password too short',))

        with self.assertRaises(AssertionError) as err:
            assert_password_properties("1234abcd")
        exc = err.exception
        self.assertEqual(exc.args, ('no uppercase character in password',))

        with self.assertRaises(AssertionError) as err:
            assert_password_properties("1234ABCD")
        exc = err.exception
        self.assertEqual(exc.args, ('no lowercase character in password',))

        with self.assertRaises(AssertionError) as err:
            assert_password_properties("ABCDabcd")
        exc = err.exception
        self.assertEqual(exc.args, ('no numeric character in password',))

        with self.assertRaises(AssertionError) as err:
            assert_password_properties("ABCabc12")
        exc = err.exception
        self.assertEqual(exc.args, ('no special character in password',))

        assert_password_properties("123abcDE+")

    def test_regenerate_api_key(self):
        with (self.app.app_context()):
            new_api_key = regenerate_api_key(USER0001_USER_ID)["api_key"]
            self.assertNotEqual(USER0001_KEY, new_api_key)
            query = select(User.api_key).where(User.id == USER0001_USER_ID)
            query_result = [pw for pw in db.session.execute(query)]
            hashed_api_key = query_result[0][0]
            self.assertEqual(1, len(query_result))
            self.assertEqual(simple_hash_str(new_api_key), hashed_api_key)

    def test_set_password(self):
        with (self.app.app_context()):
            new_password = """'.-;#Absdu23923"asLk"""

            query = select(User.password).where(User.id == USER0001_USER_ID)
            user_password_prior = [pw for pw in db.session.execute(query)][0][0]
            self.assertTrue(check_pw_str(USER0001_PASSWORD, user_password_prior))
            self.assertFalse(check_pw_str(new_password, user_password_prior))

            set_user_password(USER0001_USER_ID, new_password)

            user_password_after = [pw for pw in db.session.execute(query)][0][0]
            self.assertFalse(check_pw_str(USER0001_PASSWORD, user_password_after))
            self.assertTrue(check_pw_str(new_password, user_password_after))

    def test_check_password(self):
        with (self.app.app_context()):
            new_password = """'.-;#Absdu23923"asLk"""
            set_user_password(USER0001_USER_ID, new_password)
            self.assertTrue(check_password(USER0001_USER_ID, new_password))
            self.assertFalse(check_password(USER0001_USER_ID, new_password + 'x'))

    def test_health_check_actor(self):
        with (self.app.app_context()):
            with self.assertRaises(TypeError):
                health_check_actor(USER0001_USER_ID, 30)
            with self.assertRaises(TypeError):
                health_check_actor(ADMIN_USER_ID, 30)
            with self.assertRaises(TypeError):
                health_check_actor(DISABLED_USER_ID, 30)
            with self.assertRaises(ValueError):
                health_check_actor(ACTOR0001_USER_ID, 0)

            with mock_datetime_now(TS_12_30_00, datetime):
                self.assertFalse(health_check_actor(ACTOR0001_USER_ID, 10))
                self.assertFalse(get_state(ACTOR0001_USER_ID, ACTOR0001_USER_ID))
                self.assertTrue(health_check_actor(ACTOR0001_USER_ID, 10))
            with mock_datetime_now(TS_12_30_01, datetime):
                self.assertTrue(health_check_actor(ACTOR0001_USER_ID, 10))
            with mock_datetime_now(TS_12_30_12, datetime):
                self.assertFalse(health_check_actor(ACTOR0001_USER_ID, 10))
            with mock_datetime_now(TS_12_31_00, datetime):
                self.assertFalse(health_check_actor(ACTOR0001_USER_ID, 10))
