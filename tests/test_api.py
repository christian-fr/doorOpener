import json
import datetime
from unittest import TestCase

from flask import Config

from app import create_app, state_db, user_db, actor_db, keys_db, KeyType, now
from tests.test_fns import KEY_USER0001, KEY_USER0002, KEY_USER0003, KEY_ACTOR1, KEY_ACTOR2
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


class TestApi(TestCase):

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

    @classmethod
    def setUpClass(cls):
        cls.app = create_app(config_class=Config)
        cls.app_test = cls.app.test_client()

    @classmethod
    def tearDownClass(cls):
        pass

    def test_api(self):
        # self.create_users(self)
        self.api_get_state01(self)

    @staticmethod
    def create_users(test_case: TestCase):
        with mock_datetime_now(TS_12_30_00, datetime):
            query_string = {'api-key': KEY_ACTOR1, 'actors': '["actor1"]'}
            response = test_case.app_test.get('/api/createUser', query_string=query_string, follow_redirects=True)
            test_case.fail()

    @staticmethod
    def api_get_state01(test_case: TestCase):
        with mock_datetime_now(TS_12_30_00, datetime):
            query_string = {'api-key': KEY_ACTOR1, 'actors': '["actor1"]'}
            response = test_case.app_test.get('/api/getDoorState', query_string=query_string, follow_redirects=True)

            test_case.assertEqual({'actor1': [200, False]}, response.json)
            test_case.assertEqual(200, response.status_code)

    def test_api_set_state01(self):
        with mock_datetime_now(TS_12_30_00, datetime):
            query_string = {'api-key': KEY_ACTOR1, 'actors': '["actor1"]'}
            response = self.app_test.get('/api/getDoorState', query_string=query_string, follow_redirects=True)

            self.assertEqual({'actor1': [200, False]}, response.json)
            self.assertEqual(200, response.status_code)

        with mock_datetime_now(TS_12_30_01, datetime):
            query_string = {'api-key': KEY_USER0001, 'actors': '["actor1"]'}
            response = self.app_test.get('/api/setDoorState', query_string=query_string, follow_redirects=True)

            self.assertEqual({'actor1': 200}, response.json)
            self.assertEqual(200, response.status_code)

        with mock_datetime_now(TS_12_30_02, datetime):
            query_string = {'api-key': KEY_ACTOR1, 'actors': '["actor1"]'}
            response = self.app_test.get('/api/getDoorState', query_string=query_string, follow_redirects=True)

            self.assertEqual({'actor1': [200, True]}, response.json)
            self.assertEqual(200, response.status_code)

        with mock_datetime_now(TS_12_30_05, datetime):
            query_string = {'api-key': KEY_ACTOR1, 'actors': '["actor1"]'}
            response = self.app_test.get('/api/getDoorState', query_string=query_string, follow_redirects=True)

            self.assertEqual({'actor1': [200, True]}, response.json)
            self.assertEqual(200, response.status_code)

        with mock_datetime_now(TS_12_30_06, datetime):
            query_string = {'api-key': KEY_ACTOR1, 'actors': '["actor1"]'}
            response = self.app_test.get('/api/getDoorState', query_string=query_string, follow_redirects=True)

            self.assertEqual({'actor1': [200, False]}, response.json)
            self.assertEqual(200, response.status_code)
