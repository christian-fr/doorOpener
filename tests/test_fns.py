import datetime
import uuid
from unittest import TestCase

import flask

from app import create_app, db, Users
from app.models.users import Role
from app.util.hash import hash_salt_pw, check_pw
from config import Config
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

ACTOR0001_USER_ID = '1dad0dc3-f862-4b41-9608-2ee1fa3050c2'
ACTOR0001_KEY = '9a9893b036fd1708c518467a203de7405184feff1c2eb315ee8099cd8fedab58'

ACTOR0002_USER_ID = 'd526569c-4743-4d3e-a742-128051f63f72'
ACTOR0002_KEY = 'f160e336939ee5b8ed3206962c488fc5be3f6e35a3ca92fc170e80657958bda3'

USER0001_USER_ID = '1f4a6f9c-af4a-4a32-976d-e86a1487ec43'
USER0001_KEY = '052b3945b6913a005c74c52d0a2c48cfc7c10207db775d51950a21bc12dcc472'
USER0001_PASSWORD = 'SonneMondUndSterne'
USER0001_HASH = b'$2b$12$OIsDWfLOPdNpsXUuAUuukOgE2PBByP/CJzYY4kbmWoIYuYtwoZaXK'

USER0002_USER_ID = '72031898-24eb-46d4-b4de-40355517ef8e'
USER0002_KEY = '781bd77d28bf4c53e13719136180dcef2d54c75b37b8a3553339859255731d9d'
USER0002_PASSWORD = 'OneAndOneAndOneIsThree'
USER0002_HASH = b'$2b$12$hVZw4gxhkoIMtbjCZ1bWZ.Hv7GEIV6h3kO6mFUCZSfuZ/lEpFBB7i'

USER0003_USER_ID = 'd8977529-31bd-4f3e-b24c-91f31d962487'
USER0003_KEY = '8c267d03891a23661ec3e89dbed546297cb86bae05d4767ff01cc0b1616d3499'
USER0003_PASSWORD = 'RocknRoll'
USER0003_HASH = b'$2b$12$OIsDWfLOPdNpsXUuAUuukOgE2PBByP/CJzYY4kbmWoIYuYtwoZaXK'

USER0004_USER_ID = 'c100c404-4f65-4a23-b5d9-0979dad67fec'
USER0004_KEY = '58a0d55f80247f4b554dcae9ad274b8e96105519cd87a344bb017f42cc762b86'
USER0004_PASSWORD = 'AlleMeineEntchen'
USER0004_HASH = b'$2b$12$QBJzGrzBK5mIucCxHXfITumdGqWWzaT19H/4G7WLiWdO9qoHt9YGu'

USER0005_USER_ID = '17b6909f-565f-4416-a587-3a8791aef0e7'
USER0005_KEY = '961e67183206708d327ae766e6ac34f6ac0c082e0af8763ca8e8d3228496259a'
USER0005_PASSWORD = 'JingleBellsRock'
USER0005_HASH = b'$2b$12$81GAJhj2dPzE92rk5QwrPOKWscn/cdwOknZC8c9PIZbZ2wvZzGr0G'

USER0006_USER_ID = '9f1b6399-f051-44c3-bab3-1a4b8eb81e28'
USER0006_KEY = '535b4e070c23cca91a2044258b2f8cbabe7c58c5fe18f7a88d13c85a3c8db068'
USER0006_PASSWORD = 'SuesserDieGlockenNieKlingen'
USER0006_HASH = b'$2b$12$zH0fFDodf79ngCEnTyZccOsUYcDvS52gg7N7kv9l/qAyzfAzZXC4u'

DISABLED_USER_ID = '4c86f252-7d14-4776-a9a7-2e85e23b4f69'
DISABLED_KEY = '9c1e953d91c1bf590dcb2a6011d8f0370fd0df12baea0adfd536175596f10d43'
DISABLED_PASSWORD = 'KeinSchoenerLand'
DISABLED_HASH = b'$2b$12$7KSsl6T7igXPMUGYjxGQXOl1QKa/ax6KREZkmpdTkQoJWIyhrhBp6'

ADMIN_USER_ID = '32546de6-7c94-41b8-812b-4f5786b71e1c'
ADMIN_KEY = '98cfefb9d2c1477b3d98ebd19ec7a69bc0f82ce81a1ee88fcbdfe07a7681a829'
ADMIN_PASSWORD = 'SuperSudo'
ADMIN_HASH = b'$2b$12$Ic5poQoe.y9JW./XLGtXO.gBugpsfFVrRfHf5.6c4As9JYvVaHe3e'


def date_to_str(date: datetime.datetime) -> str:
    return date.strftime('%Y-%m-%dT%H:%M:%S.%f')


def str_to_date(date: str) -> datetime.datetime:
    return datetime.datetime.strptime(date, '%Y-%m-%dT%H:%M:%S.%f')


TS_12_29_00str = date_to_str(TS_12_29_00)
TS_12_30_06str = date_to_str(TS_12_30_06)


def set_up_testcase(app: flask.app.Flask) -> None:
    with mock_datetime_now(TS_11_00_00, datetime):
        user0001_data = {'id': uuid.UUID(USER0001_USER_ID), 'name': 'USER0001', 'email': None,
                         'password': USER0001_HASH, 'api_key': USER0001_KEY, 'role': Role.user, }
        user0002_data = {'id': uuid.UUID(USER0002_USER_ID), 'name': 'USER0002', 'email': None,
                         'password': USER0002_HASH, 'api_key': USER0002_KEY, 'role': Role.user, }
        user0003_data = {'id': uuid.UUID(USER0003_USER_ID), 'name': 'USER0003', 'email': None,
                         'password': USER0003_HASH, 'api_key': USER0003_KEY, 'role': Role.user, }
        user0004_data = {'id': uuid.UUID(USER0004_USER_ID), 'name': 'USER0004', 'email': None,
                         'password': USER0004_HASH, 'api_key': USER0004_KEY, 'role': Role.user, }
        user0005_data = {'id': uuid.UUID(USER0005_USER_ID), 'name': 'USER0005', 'email': None,
                         'password': USER0005_HASH, 'api_key': USER0005_KEY, 'role': Role.user, }
        user0006_data = {'id': uuid.UUID(USER0006_USER_ID), 'name': 'USER0006', 'email': None,
                         'password': USER0006_HASH, 'api_key': USER0006_KEY, 'role': Role.user, }
        actor0001_data = {'id': uuid.UUID(ACTOR0001_USER_ID), 'name': 'ACTOR1', 'email': None,
                          'password': None, 'api_key': ACTOR0001_KEY, 'role': Role.actor, }
        actor0002_data = {'id': uuid.UUID(ACTOR0002_USER_ID), 'name': 'ACTOR2', 'email': None,
                          'password': None, 'api_key': ACTOR0002_KEY, 'role': Role.actor, }
        disabled_data = {'id': uuid.UUID(DISABLED_USER_ID), 'name': 'DISABLED0001', 'email': None,
                         'password': DISABLED_HASH, 'api_key': DISABLED_KEY, 'role': Role.deactivated, }
        admin_data = {'id': uuid.UUID(ADMIN_USER_ID), 'name': 'ADMIN', 'email': None,
                      'password': ADMIN_HASH, 'api_key': ADMIN_KEY, 'role': Role.admin, }

        data_list = [user0001_data, user0002_data, user0003_data, user0004_data, user0005_data, user0006_data,
                     actor0001_data, actor0002_data, disabled_data, admin_data]
        created_updated_dict = {'created_at': datetime.datetime.now(), 'updated_at': datetime.datetime.now()}

        user_list = [Users(**data, **created_updated_dict) for data in data_list]
        with app.app_context():
            for user in user_list:
                db.session.add(user)
                db.session.commit()


        valid_db.insert(
            {'id': 'ac0001', 'user_id': 'ac0001', 'from': None, 'to': None, 'created_at': date_to_str(now())})
        valid_db.insert(
            {'id': 'ac0002', 'user_id': 'ac0002', 'from': None, 'to': None, 'created_at': date_to_str(now())})

        valid_db.insert(
            {'id': 'va0000', 'user_id': 'us0001', 'from': None, 'to': None, 'created_at': date_to_str(now())})
        valid_db.insert(
            {'id': 'va0001', 'user_id': 'us0002', 'from': None, 'to': None, 'created_at': date_to_str(now())})
        valid_db.insert(
            {'id': 'va0002', 'user_id': 'us0003', 'from': None, 'to': None, 'created_at': date_to_str(now())})

        valid_db.insert(
            {'id': 'va0003', 'user_id': 'us0004', 'from': None, 'to': TS_12_29_00str,
             'created_at': date_to_str(now())})
        valid_db.insert(
            {'id': 'va0004', 'user_id': 'us0005', 'from': TS_12_29_00str, 'to': TS_12_30_06str,
             'created_at': date_to_str(now())})
        valid_db.insert(
            {'id': 'va0005', 'user_id': 'us0006', 'from': TS_12_30_06str, 'to': TS_12_29_00str,
             'created_at': date_to_str(now())})

        permission_db.insert({'id': 'pe0000', 'user_id': 'ac0001', 'actor_id': 'ac0001', 'mode': 'r'})
        permission_db.insert({'id': 'pe0001', 'user_id': 'ac0002', 'actor_id': 'ac0002', 'mode': 'r'})

        permission_db.insert({'id': 'pe0002', 'user_id': 'us0001', 'actor_id': 'ac0001', 'mode': 'w'})
        permission_db.insert({'id': 'pe0003', 'user_id': 'us0002', 'actor_id': 'ac0002', 'mode': 'w'})
        permission_db.insert({'id': 'pe0004', 'user_id': 'us0003', 'actor_id': 'ac0001', 'mode': 'w'})
        permission_db.insert({'id': 'pe0005', 'user_id': 'us0003', 'actor_id': 'ac0002', 'mode': 'w'})

        keys_db.insert({'id': KEY_USER0001, 'user_id': 'us0001'})
        keys_db.insert({'id': KEY_USER0002, 'user_id': 'us0002'})
        keys_db.insert({'id': USER0003_KEY, 'user_id': 'us0003'})
        keys_db.insert({'id': ACTOR0001_KEY, 'user_id': 'ac0001'})
        keys_db.insert({'id': ACTOR0002_KEY, 'user_id': 'ac0002'})
        keys_db.insert({'id': ADMIN_KEY, 'user_id': 'ad0000'})


class ApiFunctionsTest(TestCase):
    @classmethod
    def setUpClass(cls):
        cls.app = create_app(config_class=Config)
        with cls.app.app_context():
            db.drop_all()
            db.create_all()
            db.session.commit()
        cls.app_test = cls.app.test_client()

    def setUp(self):
        set_up_testcase(self.app.app_context)

    def tearDown(self):
        pass

    def test_get_state_error(self):
        # get initial state for a wrong key
        self.assertEqual((400, {'msg': 'permission denied'}),
                         get_state(['actor1'], 'actor1e336939ee5b8ed3206962c488fc5be3f6e35a3ca92fc170e80657958bda3s'))

        # get initial state for a wrong actor id
        self.assertEqual((200, {'wxyz': (403, {'msg': 'permission denied'})}),
                         get_state(['wxyz'], ACTOR0002_KEY))

        # get initial state for an existing actor id, but with a key that is lacking permission
        self.assertEqual((200, {'ac0002': (403, {'msg': 'permission denied'})}),
                         get_state(['ac0002'], ACTOR0001_KEY))

        # this is a key that should raise an error
        key_error = '9999d77d28bf4c53e13719136180dcef2d54c75b37b8a3553339859255731d9d'

        # error tests for keys_db

        # expected behaviour for this case: should internally return a database error
        # create an empty entry for key_error in the key DB
        keys_db()[key_error] = {}
        self.assertEqual((403, {'msg': 'db error'}), get_state(['ac0002'], key_error))

    def test_check_key01(self):
        with mock_datetime_now(TS_12_30_01, datetime):
            # enable state for actor 9a98... with user 0001
            self.assertEqual((200, {'ac0001': 200}), set_state(['ac0001'], KEY_USER0001))

        with mock_datetime_now(TS_12_30_02, datetime):
            # get states for actors 9a98... and f160...
            self.assertEqual((200, {'ac0001': (200, True)}), get_state(['ac0001'], ACTOR0001_KEY))
            self.assertEqual((200, {'ac0002': (200, False)}), get_state(['ac0002'], ACTOR0002_KEY))

        with mock_datetime_now(TS_12_30_05, datetime):
            # get states for actors 9a98... and f160...
            self.assertEqual((200, {'ac0001': (200, True)}), get_state(['ac0001'], ACTOR0001_KEY))
            self.assertEqual((200, {'ac0002': (200, False)}), get_state(['ac0002'], ACTOR0002_KEY))

        with mock_datetime_now(TS_12_30_06, datetime):
            # get states for actors 9a98... and f160...
            self.assertEqual((200, {'ac0001': (200, False)}), get_state(['ac0001'], ACTOR0001_KEY))
            self.assertEqual((200, {'ac0002': (200, False)}), get_state(['ac0002'], ACTOR0002_KEY))

        with mock_datetime_now(TS_12_29_00, datetime):
            # get states for actors 9a98... and f160...
            self.assertEqual((200, {'ac0001': (200, False)}), get_state(['ac0001'], ACTOR0001_KEY))
            self.assertEqual((200, {'ac0002': (200, False)}), get_state(['ac0002'], ACTOR0002_KEY))

    def test_check_key02(self):
        with mock_datetime_now(TS_12_30_01, datetime):
            self.assertEqual((200, {'ac0002': 200}), set_state(['ac0002'], KEY_USER0002))

        with mock_datetime_now(TS_12_30_02, datetime):
            # get states for actors 9a98... and f160...
            self.assertEqual((200, {'ac0001': (200, False)}), get_state(['ac0001'], ACTOR0001_KEY))
            self.assertEqual((200, {'ac0002': (200, True)}), get_state(['ac0002'], ACTOR0002_KEY))

        with mock_datetime_now(TS_12_30_05, datetime):
            # get states for actors 9a98... and f160...
            self.assertEqual((200, {'ac0001': (200, False)}), get_state(['ac0001'], ACTOR0001_KEY))
            self.assertEqual((200, {'ac0002': (200, True)}), get_state(['ac0002'], ACTOR0002_KEY))

        with mock_datetime_now(TS_12_30_06, datetime):
            # get states for actors 9a98... and f160...
            self.assertEqual((200, {'ac0001': (200, False)}), get_state(['ac0001'], ACTOR0001_KEY))
            self.assertEqual((200, {'ac0002': (200, False)}), get_state(['ac0002'], ACTOR0002_KEY))

        # timestamps before and after the set timing should evaluate to False
        with mock_datetime_now(TS_12_29_00, datetime):
            # get states for actors 9a98... and f160...
            self.assertEqual((200, {'ac0001': (200, False)}), get_state(['ac0001'], ACTOR0001_KEY))
            self.assertEqual((200, {'ac0002': (200, False)}), get_state(['ac0002'], ACTOR0002_KEY))
        with mock_datetime_now(TS_12_30_06, datetime):
            # get states for actors 9a98... and f160...
            self.assertEqual((200, {'ac0001': (200, False)}), get_state(['ac0001'], ACTOR0001_KEY))
            self.assertEqual((200, {'ac0002': (200, False)}), get_state(['ac0002'], ACTOR0002_KEY))

    def test_check_key03(self):
        with mock_datetime_now(TS_12_30_01, datetime):
            # enable state for actor 9a98... and f160... with user 0003
            self.assertEqual((200, {'ac0001': 200, 'ac0002': 200}), set_state(['ac0001', 'ac0002'], USER0003_KEY))

            # check the state
            self.assertEqual((200, {'ac0001': (200, True)}), get_state(['ac0001'], ACTOR0001_KEY))
            self.assertEqual((200, {'ac0002': (200, True)}), get_state(['ac0002'], ACTOR0002_KEY))

        with mock_datetime_now(TS_12_30_02, datetime):
            # get states for actors 9a98... and f160...
            self.assertEqual((200, {'ac0001': (200, True)}), get_state(['ac0001'], ACTOR0001_KEY))
            self.assertEqual((200, {'ac0002': (200, True)}), get_state(['ac0002'], ACTOR0002_KEY))

        with mock_datetime_now(TS_12_30_05, datetime):
            # get states for actors 9a98... and f160...
            self.assertEqual((200, {'ac0001': (200, True)}), get_state(['ac0001'], ACTOR0001_KEY))
            self.assertEqual((200, {'ac0002': (200, True)}), get_state(['ac0002'], ACTOR0002_KEY))

        with mock_datetime_now(TS_12_30_06, datetime):
            # get states for actors 9a98... and f160...
            self.assertEqual((200, {'ac0001': (200, False)}), get_state(['ac0001'], ACTOR0001_KEY))
            self.assertEqual((200, {'ac0002': (200, False)}), get_state(['ac0002'], ACTOR0002_KEY))

        # timestamps before and after the set timing should evaluate to False
        with mock_datetime_now(TS_12_29_00, datetime):
            # get states for actors 9a98... and f160...
            self.assertEqual((200, {'ac0001': (200, False)}), get_state(['ac0001'], ACTOR0001_KEY))
            self.assertEqual((200, {'ac0002': (200, False)}), get_state(['ac0002'], ACTOR0002_KEY))
        with mock_datetime_now(TS_12_30_06, datetime):
            # get states for actors 9a98... and f160...
            self.assertEqual((200, {'ac0001': (200, False)}), get_state(['ac0001'], ACTOR0001_KEY))
            self.assertEqual((200, {'ac0002': (200, False)}), get_state(['ac0002'], ACTOR0002_KEY))

    def test_sanitize_state_db(self):
        with mock_datetime_now(TS_12_30_00, datetime):
            # enable state for actor ac0001 with user us0001
            self.assertEqual((200, {'ac0001': 200}), set_state(['ac0001'], KEY_USER0001))

        with mock_datetime_now(TS_12_30_04, datetime):
            # get initial state for actor ac0001
            self.assertEqual((200, {'ac0001': (200, True)}), get_state(['ac0001'], ACTOR0001_KEY))

            # manually set last_on to a future date
            state_db()['ac0001']['last_on'] = TS_12_31_00
        db = state_db().copy()
        with mock_datetime_now(TS_12_30_06, datetime):
            # check if sanitazation works as expected (state will be set to None, thereby evaluating to false below
            # assert that second actor is still false
            self.assertEqual((200, {'ac0002': (200, False)}), get_state(['ac0002'], ACTOR0002_KEY))
            self.assertEqual((200, {'ac0001': (200, False)}), get_state(['ac0001'], ACTOR0001_KEY))

            db = state_db().copy()
            # check that the future timestamp is in state_db()
            self.assertEqual({'ac0001': {'last_on': TS_12_31_00}}, state_db())
            # iterate 10 times to trigger the sanitization
            [get_state(['ac0001'], ACTOR0001_KEY) for _ in range(10)]
            # check that the future timestamp is set to None
            self.assertEqual({'ac0001': {'last_on': None}}, state_db())
            # ... which should evaluate to False on the get_state endpoint
            self.assertEqual((200, {'ac0001': (200, False)}), get_state(['ac0001'], ACTOR0001_KEY))

    def test_create_user(self):
        user_id = '0123testuser6789'
        self.assertNotIn(user_id, user_db())
        result = create_user_helper(api_key=ADMIN_KEY, user_id=user_id, name='testUser', role=Role.USER,
                                    valid_from=TS_11_00_00, valid_until=TS_16_00_00)
        self.assertEqual((200, {'msg': 'user created', 'user-id': '0123testuser6789'}), result)
        self.assertIn(user_id, user_db())
        self.assertEqual({'name': 'testUser', 'role': Role.USER, 'valid_from': TS_11_00_00, 'valid_until': TS_16_00_00,
                          'timeout': None}, user_db()[user_id])

    def test_create_user_key(self):
        user_id = create_user_helper(api_key=ADMIN_KEY, name='testUser', role=Role.USER, valid_from=TS_11_00_00,
                                     valid_until=TS_16_00_00)[1]['user-id']
        api_key = create_user_key(user_id)[1]['api-key']
        self.assertEqual({'user_id': user_id}, keys_db()[api_key])

    def test_list_api_keys(self):
        result = list_api_keys_helper(ADMIN_KEY)
        self.assertEqual(200, result[0])
        api_keys = result[1]['api-keys-truncated']
        self.assertEqual({'052b39', '781bd7', '8c267d', '9a9893', 'f160e3'}, set(api_keys))
