import datetime
from unittest import TestCase
from app import user_db, keys_db, state_db, valid_db, permission_db, get_state, set_state, create_user, create_user_key, \
    Role, now
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

KEY_ACTOR1 = '9a9893b036fd1708c518467a203de7405184feff1c2eb315ee8099cd8fedab58'
KEY_ACTOR2 = 'f160e336939ee5b8ed3206962c488fc5be3f6e35a3ca92fc170e80657958bda3'
KEY_USER0001 = '052b3945b6913a005c74c52d0a2c48cfc7c10207db775d51950a21bc12dcc472'
KEY_USER0002 = '781bd77d28bf4c53e13719136180dcef2d54c75b37b8a3553339859255731d9d'
KEY_USER0003 = '8c267d03891a23661ec3e89dbed546297cb86bae05d4767ff01cc0b1616d3499'
KEY_ADMIN = '98cfefb9d2c1477b3d98ebd19ec7a69bc0f82ce81a1ee88fcbdfe07a7681a829'


def set_up_testcase() -> None:
    with mock_datetime_now(TS_11_00_00, datetime):
        keys_db().clear()
        user_db().clear()
        state_db().clear()
        permission_db().clear()
        valid_db().clear()

        user_db()['ad0000'] = {'name': 'test admin', 'role': Role.ADMIN, 'timeout': None}

        user_db()['us0001'] = {'name': 'test user 1', 'role': Role.USER, 'timeout': None}
        user_db()['us0002'] = {'name': 'test user 2', 'role': Role.USER, 'timeout': None}
        user_db()['us0003'] = {'name': 'test user 3', 'role': Role.USER, 'timeout': None}

        user_db()['us0004'] = {'name': 'test user 4', 'role': Role.USER, 'timeout': None}
        user_db()['us0005'] = {'name': 'test user 5', 'role': Role.USER, 'timeout': None}
        user_db()['us0006'] = {'name': 'test user 6', 'role': Role.USER, 'timeout': None}

        user_db()['ac0001'] = {'name': 'test actor 1', 'role': Role.ACTOR, 'timeout': 5}
        user_db()['ac0002'] = {'name': 'test actor 1', 'role': Role.ACTOR, 'timeout': 5}

        user_db()['di0003'] = {'name': 'test user disabled', 'role': Role.DISABLED, 'timeout': None}

        valid_db()['ac0001'] = {'user_id': 'ac0001', 'from': None, 'to': None, 'created_at': now()}
        valid_db()['ac0002'] = {'user_id': 'ac0002', 'from': None, 'to': None, 'created_at': now()}

        valid_db()['va0000'] = {'user_id': 'us0001', 'from': None, 'to': None, 'created_at': now()}
        valid_db()['va0001'] = {'user_id': 'us0002', 'from': None, 'to': None, 'created_at': now()}
        valid_db()['va0002'] = {'user_id': 'us0003', 'from': None, 'to': None, 'created_at': now()}

        valid_db()['va0003'] = {'user_id': 'us0004', 'from': None, 'to': TS_12_29_00, 'created_at': now()}
        valid_db()['va0004'] = {'user_id': 'us0005', 'from': TS_12_29_00, 'to': TS_12_30_06, 'created_at': now()}
        valid_db()['va0005'] = {'user_id': 'us0006', 'from': TS_12_30_06, 'to': TS_12_29_00, 'created_at': now()}

        permission_db()['pe0000'] = {'user_id': 'ac0001', 'actor_id': 'ac0001', 'mode': 'r'}
        permission_db()['pe0001'] = {'user_id': 'ac0002', 'actor_id': 'ac0002', 'mode': 'r'}

        permission_db()['pe0002'] = {'user_id': 'us0001', 'actor_id': 'ac0001', 'mode': 'w'}
        permission_db()['pe0003'] = {'user_id': 'us0002', 'actor_id': 'ac0002', 'mode': 'w'}
        permission_db()['pe0004'] = {'user_id': 'us0003', 'actor_id': 'ac0001', 'mode': 'w'}
        permission_db()['pe0005'] = {'user_id': 'us0003', 'actor_id': 'ac0002', 'mode': 'w'}

        keys_db()[KEY_USER0001] = {'user_id': 'us0001'}
        keys_db()[KEY_USER0002] = {'user_id': 'us0002'}
        keys_db()[KEY_USER0003] = {'user_id': 'us0003'}
        keys_db()[KEY_ACTOR1] = {'user_id': 'ac0001'}
        keys_db()[KEY_ACTOR2] = {'user_id': 'ac0002'}
        keys_db()[KEY_ADMIN] = {'user_id': 'ad0000'}


class ApiFunctionsTest(TestCase):
    def setUp(self):
        set_up_testcase()

    def tearDown(self):
        pass

    def test_get_state_error(self):
        # get initial state for a wrong key
        self.assertEqual((400, {'msg': 'permission denied'}),
                         get_state(['actor1'], 'actor1e336939ee5b8ed3206962c488fc5be3f6e35a3ca92fc170e80657958bda3s'))

        # get initial state for a wrong actor id
        self.assertEqual((200, {'wxyz': (403, {'msg': 'permission denied'})}),
                         get_state(['wxyz'], KEY_ACTOR2))

        # get initial state for an existing actor id, but with a key that is lacking permission
        self.assertEqual((200, {'ac0002': (403, {'msg': 'permission denied'})}),
                         get_state(['ac0002'], KEY_ACTOR1))

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
            self.assertEqual((200, {'ac0001': (200, True)}), get_state(['ac0001'], KEY_ACTOR1))
            self.assertEqual((200, {'ac0002': (200, False)}), get_state(['ac0002'], KEY_ACTOR2))

        with mock_datetime_now(TS_12_30_05, datetime):
            # get states for actors 9a98... and f160...
            self.assertEqual((200, {'ac0001': (200, True)}), get_state(['ac0001'], KEY_ACTOR1))
            self.assertEqual((200, {'ac0002': (200, False)}), get_state(['ac0002'], KEY_ACTOR2))

        with mock_datetime_now(TS_12_30_06, datetime):
            # get states for actors 9a98... and f160...
            self.assertEqual((200, {'ac0001': (200, False)}), get_state(['ac0001'], KEY_ACTOR1))
            self.assertEqual((200, {'ac0002': (200, False)}), get_state(['ac0002'], KEY_ACTOR2))

        with mock_datetime_now(TS_12_29_00, datetime):
            # get states for actors 9a98... and f160...
            self.assertEqual((200, {'ac0001': (200, False)}), get_state(['ac0001'], KEY_ACTOR1))
            self.assertEqual((200, {'ac0002': (200, False)}), get_state(['ac0002'], KEY_ACTOR2))

    def test_check_key02(self):
        with mock_datetime_now(TS_12_30_01, datetime):
            self.assertEqual((200, {'ac0002': 200}), set_state(['ac0002'], KEY_USER0002))

        with mock_datetime_now(TS_12_30_02, datetime):
            # get states for actors 9a98... and f160...
            self.assertEqual((200, {'ac0001': (200, False)}), get_state(['ac0001'], KEY_ACTOR1))
            self.assertEqual((200, {'ac0002': (200, True)}), get_state(['ac0002'], KEY_ACTOR2))

        with mock_datetime_now(TS_12_30_05, datetime):
            # get states for actors 9a98... and f160...
            self.assertEqual((200, {'ac0001': (200, False)}), get_state(['ac0001'], KEY_ACTOR1))
            self.assertEqual((200, {'ac0002': (200, True)}), get_state(['ac0002'], KEY_ACTOR2))

        with mock_datetime_now(TS_12_30_06, datetime):
            # get states for actors 9a98... and f160...
            self.assertEqual((200, {'ac0001': (200, False)}), get_state(['ac0001'], KEY_ACTOR1))
            self.assertEqual((200, {'ac0002': (200, False)}), get_state(['ac0002'], KEY_ACTOR2))

        # timestamps before and after the set timing should evaluate to False
        with mock_datetime_now(TS_12_29_00, datetime):
            # get states for actors 9a98... and f160...
            self.assertEqual((200, {'ac0001': (200, False)}), get_state(['ac0001'], KEY_ACTOR1))
            self.assertEqual((200, {'ac0002': (200, False)}), get_state(['ac0002'], KEY_ACTOR2))
        with mock_datetime_now(TS_12_30_06, datetime):
            # get states for actors 9a98... and f160...
            self.assertEqual((200, {'ac0001': (200, False)}), get_state(['ac0001'], KEY_ACTOR1))
            self.assertEqual((200, {'ac0002': (200, False)}), get_state(['ac0002'], KEY_ACTOR2))

    def test_check_key03(self):
        with mock_datetime_now(TS_12_30_01, datetime):
            # enable state for actor 9a98... and f160... with user 0003
            self.assertEqual((200, {'ac0001': 200, 'ac0002': 200}), set_state(['ac0001', 'ac0002'], KEY_USER0003))

            # check the state
            self.assertEqual((200, {'ac0001': (200, True)}), get_state(['ac0001'], KEY_ACTOR1))
            self.assertEqual((200, {'ac0002': (200, True)}), get_state(['ac0002'], KEY_ACTOR2))

        with mock_datetime_now(TS_12_30_02, datetime):
            # get states for actors 9a98... and f160...
            self.assertEqual((200, {'ac0001': (200, True)}), get_state(['ac0001'], KEY_ACTOR1))
            self.assertEqual((200, {'ac0002': (200, True)}), get_state(['ac0002'], KEY_ACTOR2))

        with mock_datetime_now(TS_12_30_05, datetime):
            # get states for actors 9a98... and f160...
            self.assertEqual((200, {'ac0001': (200, True)}), get_state(['ac0001'], KEY_ACTOR1))
            self.assertEqual((200, {'ac0002': (200, True)}), get_state(['ac0002'], KEY_ACTOR2))

        with mock_datetime_now(TS_12_30_06, datetime):
            # get states for actors 9a98... and f160...
            self.assertEqual((200, {'ac0001': (200, False)}), get_state(['ac0001'], KEY_ACTOR1))
            self.assertEqual((200, {'ac0002': (200, False)}), get_state(['ac0002'], KEY_ACTOR2))

        # timestamps before and after the set timing should evaluate to False
        with mock_datetime_now(TS_12_29_00, datetime):
            # get states for actors 9a98... and f160...
            self.assertEqual((200, {'ac0001': (200, False)}), get_state(['ac0001'], KEY_ACTOR1))
            self.assertEqual((200, {'ac0002': (200, False)}), get_state(['ac0002'], KEY_ACTOR2))
        with mock_datetime_now(TS_12_30_06, datetime):
            # get states for actors 9a98... and f160...
            self.assertEqual((200, {'ac0001': (200, False)}), get_state(['ac0001'], KEY_ACTOR1))
            self.assertEqual((200, {'ac0002': (200, False)}), get_state(['ac0002'], KEY_ACTOR2))

    def test_sanitize_state_db(self):
        with mock_datetime_now(TS_12_30_00, datetime):
            # enable state for actor ac0001 with user us0001
            self.assertEqual((200, {'ac0001': 200}), set_state(['ac0001'], KEY_USER0001))

        with mock_datetime_now(TS_12_30_04, datetime):
            # get initial state for actor ac0001
            self.assertEqual((200, {'ac0001': (200, True)}), get_state(['ac0001'], KEY_ACTOR1))

            # manually set last_on to a future date
            state_db()['ac0001']['last_on'] = TS_12_31_00
        db = state_db().copy()
        with mock_datetime_now(TS_12_30_06, datetime):
            # check if sanitazation works as expected (state will be set to None, thereby evaluating to false below
            # assert that second actor is still false
            self.assertEqual((200, {'ac0002': (200, False)}), get_state(['ac0002'], KEY_ACTOR2))
            self.assertEqual((200, {'ac0001': (200, False)}), get_state(['ac0001'], KEY_ACTOR1))

            db = state_db().copy()
            # check that the future timestamp is in state_db()
            self.assertEqual({'ac0001': {'last_on': TS_12_31_00}}, state_db())
            # iterate 10 times to trigger the sanitization
            [get_state(['ac0001'], KEY_ACTOR1) for _ in range(10)]
            # check that the future timestamp is set to None
            self.assertEqual({'ac0001': {'last_on': None}}, state_db())
            # ... which should evaluate to False on the get_state endpoint
            self.assertEqual((200, {'ac0001': (200, False)}), get_state(['ac0001'], KEY_ACTOR1))

    def test_create_user(self):
        user_id = '0123testuser6789'
        self.assertNotIn(user_id, user_db())
        result = create_user(name='testUser', actor_ids=[], user_id=user_id)
        self.assertEqual((200, {'msg': 'user created', 'user-id': '0123testuser6789'}), result)
        self.assertIn(user_id, user_db())
        self.assertEqual({'name': 'testUser', 'actor_ids': [], 'valid_from': None, 'valid_until': None},
                         user_db()[user_id])

    def test_create_user_key(self):
        user_id = create_user(name='testUser', actor_ids=['ac0001'])[1]['user-id']
        api_key = create_user_key(user_id)[1]['api-key']
        self.assertEqual({'user_id': user_id}, keys_db()[api_key])
