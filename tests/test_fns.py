import datetime
from unittest import TestCase
from app import user_db, keys_db, actor_db, state_db, KeyType, get_state, set_state
from tests.util.mock_datetime import mock_datetime_now

TS_11_00_00 = datetime.datetime(year=2024, month=2, day=20, hour=11, minute=0, second=0)
TS_12_29_00 = datetime.datetime(year=2024, month=2, day=20, hour=12, minute=29, second=0)
TS_12_30_00 = datetime.datetime(year=2024, month=2, day=20, hour=12, minute=30, second=0)
TS_12_30_01 = datetime.datetime(year=2024, month=2, day=20, hour=12, minute=30, second=1)
TS_12_30_02 = datetime.datetime(year=2024, month=2, day=20, hour=12, minute=30, second=2)
TS_12_30_03 = datetime.datetime(year=2024, month=2, day=20, hour=12, minute=30, second=3)
TS_12_30_04 = datetime.datetime(year=2024, month=2, day=20, hour=12, minute=30, second=4)
TS_12_30_05 = datetime.datetime(year=2024, month=2, day=20, hour=12, minute=30, second=5)
TS_12_30_06 = datetime.datetime(year=2024, month=2, day=20, hour=12, minute=30, second=6)
TS_12_30_07 = datetime.datetime(year=2024, month=2, day=20, hour=12, minute=30, second=7)
TS_12_30_08 = datetime.datetime(year=2024, month=2, day=20, hour=12, minute=30, second=8)
TS_12_30_09 = datetime.datetime(year=2024, month=2, day=20, hour=12, minute=30, second=9)
TS_12_30_10 = datetime.datetime(year=2024, month=2, day=20, hour=12, minute=30, second=10)
TS_12_30_11 = datetime.datetime(year=2024, month=2, day=20, hour=12, minute=30, second=11)
TS_12_30_12 = datetime.datetime(year=2024, month=2, day=20, hour=12, minute=30, second=12)
TS_12_31_00 = datetime.datetime(year=2024, month=2, day=20, hour=12, minute=31, second=0)
TS_16_00_00 = datetime.datetime(year=2024, month=2, day=20, hour=16, minute=0, second=0)

KEY_ACTOR1 = '9a9893b036fd1708c518467a203de7405184feff1c2eb315ee8099cd8fedab58'
KEY_ACTOR2 = 'f160e336939ee5b8ed3206962c488fc5be3f6e35a3ca92fc170e80657958bda3'
KEY_USER0001 = '052b3945b6913a005c74c52d0a2c48cfc7c10207db775d51950a21bc12dcc472'
KEY_USER0002 = '781bd77d28bf4c53e13719136180dcef2d54c75b37b8a3553339859255731d9d'
KEY_USER0003 = '8c267d03891a23661ec3e89dbed546297cb86bae05d4767ff01cc0b1616d3499'


class ApiFunctionsTest(TestCase):
    def setUp(self):
        keys_db().clear()
        user_db().clear()
        actor_db().clear()
        state_db().clear()

        keys_db()[KEY_USER0001] = {
            'type': KeyType.USER, 'ref_id': '0001'}
        keys_db()[KEY_USER0002] = {
            'type': KeyType.USER, 'ref_id': '0002'}
        keys_db()[KEY_USER0003] = {
            'type': KeyType.USER, 'ref_id': '0003'}
        keys_db()[KEY_ACTOR1] = {
            'type': KeyType.ACTOR, 'ref_id': 'actor1'}
        keys_db()[KEY_ACTOR2] = {
            'type': KeyType.ACTOR, 'ref_id': 'actor2'}

        user_db()['0001'] = {'actor_ids': ['actor1'], 'valid_from': None, 'valid_until': None}
        user_db()['0002'] = {'actor_ids': ['actor2'], 'valid_from': None, 'valid_until': None}
        user_db()['0003'] = {'actor_ids': ['actor1', 'actor2'], 'valid_from': None, 'valid_until': None}

        user_db()['0004'] = {'actor_ids': ['actor1', 'actor2'], 'valid_from': None,
                             'valid_until': TS_12_29_00}
        user_db()['0005'] = {'actor_ids': ['actor1', 'actor2'], 'valid_from': TS_12_29_00,
                             'valid_until': TS_12_30_06}
        user_db()['0006'] = {'actor_ids': ['actor1', 'actor2'], 'valid_from': TS_12_30_06,
                             'valid_until': TS_12_29_00}

        actor_db()['actor1'] = {'name': 'door street', 'timeout': 5}
        actor_db()['actor2'] = {'name': 'door flat', 'timeout': 5}

    def tearDown(self):
        pass

    def test_get_state_error(self):
        # get initial state for a wrong key
        self.assertEqual((400, {'msg': 'permission denied'}),
                         get_state(['actor1'], 'actor1e336939ee5b8ed3206962c488fc5be3f6e35a3ca92fc170e80657958bda3'))

        # get initial state for a wrong actor id
        self.assertEqual((200, {'wxyz': (400, False)}),
                         get_state(['wxyz'], KEY_ACTOR2))

        # get initial state for an existing actor id, but with a key that is lacking permission
        self.assertEqual((200, {'actor2': (200, False)}),
                         get_state(['actor2'], KEY_ACTOR1))

        # this is a key that should raise an error
        key_error = '9999d77d28bf4c53e13719136180dcef2d54c75b37b8a3553339859255731d9d'

        # error tests for keys_db
        # expected behaviour for all three cases: should internally return a database error

        # create an empty entry for key_error in the key DB
        keys_db()[key_error] = {}
        self.assertEqual((403, {'msg': 'db error'}), get_state(['actor2'], key_error))

        # set only key type, omit ref_id for key_error
        keys_db()[key_error] = {'type': KeyType.USER}
        self.assertEqual((403, {'msg': 'db error'}), get_state(['actor2'], key_error))

        # set only ref_id, omit key type for key_error
        keys_db()[key_error] = {'ref_id': '0002'}
        self.assertEqual((403, {'msg': 'db error'}), get_state(['actor2'], key_error))

    def test_check_key01(self):
        with mock_datetime_now(TS_12_30_01, datetime):
            # enable state for actor 9a98... with user 0001
            self.assertEqual((200, {'actor1': 200}), set_state(['actor1'], KEY_USER0001))

        with mock_datetime_now(TS_12_30_02, datetime):
            # get states for actors 9a98... and f160...
            self.assertEqual((200, {'actor1': (200, True)}), get_state(['actor1'], KEY_ACTOR1))
            self.assertEqual((200, {'actor2': (200, False)}), get_state(['actor2'], KEY_ACTOR2))

        with mock_datetime_now(TS_12_30_05, datetime):
            # get states for actors 9a98... and f160...
            self.assertEqual((200, {'actor1': (200, True)}), get_state(['actor1'], KEY_ACTOR1))
            self.assertEqual((200, {'actor2': (200, False)}), get_state(['actor2'], KEY_ACTOR2))

        with mock_datetime_now(TS_12_30_06, datetime):
            # get states for actors 9a98... and f160...
            self.assertEqual((200, {'actor1': (200, False)}), get_state(['actor1'], KEY_ACTOR1))
            self.assertEqual((200, {'actor2': (200, False)}), get_state(['actor2'], KEY_ACTOR2))

        with mock_datetime_now(TS_12_29_00, datetime):
            # get states for actors 9a98... and f160...
            self.assertEqual((200, {'actor1': (200, False)}), get_state(['actor1'], KEY_ACTOR1))
            self.assertEqual((200, {'actor2': (200, False)}), get_state(['actor2'], KEY_ACTOR2))

    def test_check_key02(self):
        with mock_datetime_now(TS_12_30_01, datetime):
            self.assertEqual((200, {'actor2': 200}), set_state(['actor2'], KEY_USER0002))

        with mock_datetime_now(TS_12_30_02, datetime):
            # get states for actors 9a98... and f160...
            self.assertEqual((200, {'actor1': (200, False)}), get_state(['actor1'], KEY_ACTOR1))
            self.assertEqual((200, {'actor2': (200, True)}), get_state(['actor2'], KEY_ACTOR2))

        with mock_datetime_now(TS_12_30_05, datetime):
            # get states for actors 9a98... and f160...
            self.assertEqual((200, {'actor1': (200, False)}), get_state(['actor1'], KEY_ACTOR1))
            self.assertEqual((200, {'actor2': (200, True)}), get_state(['actor2'], KEY_ACTOR2))

        with mock_datetime_now(TS_12_30_06, datetime):
            # get states for actors 9a98... and f160...
            self.assertEqual((200, {'actor1': (200, False)}), get_state(['actor1'], KEY_ACTOR1))
            self.assertEqual((200, {'actor2': (200, False)}), get_state(['actor2'], KEY_ACTOR2))

        # timestamps before and after the set timing should evaluate to False
        with mock_datetime_now(TS_12_29_00, datetime):
            # get states for actors 9a98... and f160...
            self.assertEqual((200, {'actor1': (200, False)}), get_state(['actor1'], KEY_ACTOR1))
            self.assertEqual((200, {'actor2': (200, False)}), get_state(['actor2'], KEY_ACTOR2))
        with mock_datetime_now(TS_12_30_06, datetime):
            # get states for actors 9a98... and f160...
            self.assertEqual((200, {'actor1': (200, False)}), get_state(['actor1'], KEY_ACTOR1))
            self.assertEqual((200, {'actor2': (200, False)}), get_state(['actor2'], KEY_ACTOR2))

    def test_check_key03(self):
        with mock_datetime_now(TS_12_30_01, datetime):
            # enable state for actor 9a98... and f160... with user 0003
            self.assertEqual((200, {'actor1': 200, 'actor2': 200}), set_state(['actor1', 'actor2'], KEY_USER0003))

            # check the state
            self.assertEqual((200, {'actor1': (200, True)}), get_state(['actor1'], KEY_ACTOR1))
            self.assertEqual((200, {'actor2': (200, True)}), get_state(['actor2'], KEY_ACTOR2))

        with mock_datetime_now(TS_12_30_02, datetime):
            # get states for actors 9a98... and f160...
            self.assertEqual((200, {'actor1': (200, True)}), get_state(['actor1'], KEY_ACTOR1))
            self.assertEqual((200, {'actor2': (200, True)}), get_state(['actor2'], KEY_ACTOR2))

        with mock_datetime_now(TS_12_30_05, datetime):
            # get states for actors 9a98... and f160...
            self.assertEqual((200, {'actor1': (200, True)}), get_state(['actor1'], KEY_ACTOR1))
            self.assertEqual((200, {'actor2': (200, True)}), get_state(['actor2'], KEY_ACTOR2))

        with mock_datetime_now(TS_12_30_06, datetime):
            # get states for actors 9a98... and f160...
            self.assertEqual((200, {'actor1': (200, False)}), get_state(['actor1'], KEY_ACTOR1))
            self.assertEqual((200, {'actor2': (200, False)}), get_state(['actor2'], KEY_ACTOR2))

        # timestamps before and after the set timing should evaluate to False
        with mock_datetime_now(TS_12_29_00, datetime):
            # get states for actors 9a98... and f160...
            self.assertEqual((200, {'actor1': (200, False)}), get_state(['actor1'], KEY_ACTOR1))
            self.assertEqual((200, {'actor2': (200, False)}), get_state(['actor2'], KEY_ACTOR2))
        with mock_datetime_now(TS_12_30_06, datetime):
            # get states for actors 9a98... and f160...
            self.assertEqual((200, {'actor1': (200, False)}), get_state(['actor1'], KEY_ACTOR1))
            self.assertEqual((200, {'actor2': (200, False)}), get_state(['actor2'], KEY_ACTOR2))

    def test_sanitize_state_db(self):
        with mock_datetime_now(TS_12_30_00, datetime):
            # enable state for actor 9a98... with user 0001
            self.assertEqual((200, {'actor1': 200}), set_state(['actor1'], KEY_USER0001))

        with mock_datetime_now(TS_12_30_04, datetime):
            # get initial state for actor 9a98..
            self.assertEqual((200, {'actor1': (200, True)}), get_state(['actor1'], KEY_ACTOR1))

            # manually set last_on to a future date
            state_db()['actor1']['last_on'] = TS_12_31_00

        with mock_datetime_now(TS_12_30_06, datetime):
            # check if sanitazation works as expected (state will be set to None, thereby evaluating to false below
            # assert that second actor is still false
            self.assertEqual((200, {'actor2': (200, False)}), get_state(['actor2'], KEY_ACTOR2))
            self.assertEqual((200, {'actor1': (200, False)}), get_state(['actor1'], KEY_ACTOR1))

            # check that the future timestamp is in state_db()
            self.assertEqual({'actor1': {'last_on': TS_12_31_00}}, state_db())
            # iterate 10 times to trigger the sanitization
            [get_state(['actor1'], KEY_ACTOR1) for _ in range(10)]
            # check that the future timestamp is set to None
            self.assertEqual({'actor1': {'last_on': None}}, state_db())
            # ... which should evaluate to False on the get_state endpoint
            self.assertEqual((200, {'actor1': (200, False)}), get_state(['actor1'], KEY_ACTOR1))
