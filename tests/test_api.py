import datetime
import json
from pathlib import Path
from unittest import TestCase
import os

from app import create_app, db

from tests.context.testfixture_config import Config

from tests.test_fns import (USER0002_KEY, ACTOR0001_KEY, ACTOR0002_KEY, TS_11_00_00, TS_12_29_00, TS_12_30_00,
                            TS_12_30_01, TS_12_30_02, TS_12_30_03, TS_12_30_04, TS_12_30_05, TS_12_30_06, TS_12_30_07,
                            TS_12_30_08, TS_12_30_09, TS_12_30_10, TS_12_30_11, TS_12_30_12, set_up_users, set_up_valid,
                            set_up_scope, set_up_state, ACTOR0002_USER_ID, ACTOR0001_USER_ID, ACTOR0003_USER_ID,
                            ACTOR0003_KEY)
from tests.util.mock_datetime import mock_datetime_now


class TestApiEndpoints(TestCase):
    def setUp(self):
        self.app = create_app(config_class=Config)
        with self.app.app_context():
            db.drop_all()
            db.create_all()
            db.session.commit()
        self.app_test = self.app.test_client()

        set_up_users(self.app, TS_11_00_00)
        set_up_valid(self.app, TS_11_00_00)
        set_up_scope(self.app, TS_11_00_00)

    def tearDown(self):
        with self.app.app_context():
            db.drop_all()

        if 'SQLALCHEMY_DATABASE_URI' in self.app.config:
            db_path = self.app.config['SQLALCHEMY_DATABASE_URI']
            if db_path.startswith('sqlite:///') and db_path.endswith('test.sqlite'):
                db_path_file = Path(db_path[len('sqlite:///'):])
                if db_path_file.exists():
                    os.remove(db_path_file)

    def test_set_state(self):
        for ts in [TS_12_29_00, TS_12_30_00, TS_12_30_01, TS_12_30_02, TS_12_30_02, TS_12_30_03, TS_12_30_04,
                   TS_12_30_05, TS_12_30_06, TS_12_30_07, TS_12_30_08, TS_12_30_09, TS_12_30_10, TS_12_30_11,
                   TS_12_30_12]:
            with mock_datetime_now(ts, datetime):
                query_string = {'api-key': ACTOR0002_KEY, 'actors': json.dumps([ACTOR0002_USER_ID])}
                response = self.app_test.get('/api/getState', query_string=query_string, follow_redirects=True)
                self.assertEqual(200, response.status_code)
                self.assertEqual({ACTOR0002_USER_ID: [200, {'state': False}]}, response.json)

        with mock_datetime_now(TS_12_30_01, datetime):
            query_string = {'api-key': USER0002_KEY, 'actors': json.dumps([ACTOR0002_USER_ID])}
            response = self.app_test.get('/api/setState', query_string=query_string, follow_redirects=True)
            self.assertEqual(200, response.status_code)
            self.assertEqual({ACTOR0002_USER_ID: [200, {'msg': 'success'}]}, response.json)

        for ts in [TS_12_29_00, TS_12_30_00, TS_12_30_12]:
            with mock_datetime_now(ts, datetime):
                query_string = {'api-key': ACTOR0002_KEY, 'actors': json.dumps([ACTOR0002_USER_ID])}
                response = self.app_test.get('/api/getState', query_string=query_string, follow_redirects=True)
                self.assertEqual(200, response.status_code)
                self.assertEqual({ACTOR0002_USER_ID: [200, {'state': False}]}, response.json)

        for ts in [TS_12_30_01, TS_12_30_02, TS_12_30_02, TS_12_30_03, TS_12_30_04, TS_12_30_05, TS_12_30_06,
                   TS_12_30_07, TS_12_30_08, TS_12_30_09, TS_12_30_10, TS_12_30_11, ]:
            with mock_datetime_now(ts, datetime):
                query_string = {'api-key': ACTOR0002_KEY, 'actors': json.dumps([ACTOR0002_USER_ID])}
                response = self.app_test.get('/api/getState', query_string=query_string, follow_redirects=True)
                self.assertEqual(200, response.status_code)
                self.assertEqual({ACTOR0002_USER_ID: [200, {'state': True}]}, response.json)

    def test_get_state(self):
        # initially set up state table
        set_up_state(self.app, TS_11_00_00)

        with self.app.app_context():
            for ts in [TS_12_30_02, TS_12_30_11, TS_12_30_12]:
                with mock_datetime_now(ts, datetime):
                    query_string = {'api-key': ACTOR0001_KEY, 'actors': json.dumps([ACTOR0001_USER_ID])}
                    response = self.app_test.get('/api/getState', query_string=query_string, follow_redirects=True)
                    self.assertEqual(200, response.status_code)
                    self.assertEqual({ACTOR0001_USER_ID: [200, {'state': False}]}, response.json)

            for ts in [TS_12_30_01, TS_12_30_03, TS_12_30_04, TS_12_30_05, TS_12_30_06, TS_12_30_07, TS_12_30_08,
                       TS_12_30_09, TS_12_30_10]:
                with mock_datetime_now(ts, datetime):
                    query_string = {'api-key': ACTOR0001_KEY, 'actors': json.dumps([ACTOR0001_USER_ID])}
                    response = self.app_test.get('/api/getState', query_string=query_string, follow_redirects=True)
                    self.assertEqual(200, response.status_code)
                    self.assertEqual({ACTOR0001_USER_ID: [200, {'state': True}]}, response.json)

            # more than one actor in list
            for ts in [TS_12_29_00, TS_12_30_04]:
                with mock_datetime_now(ts, datetime):
                    query_string = {'api-key': ACTOR0001_KEY,
                                    'actors': json.dumps([ACTOR0001_USER_ID, ACTOR0002_USER_ID])}
                    response = self.app_test.get('/api/getState', query_string=query_string, follow_redirects=True)
                    self.assertEqual(200, response.status_code)
                    self.assertEqual({ACTOR0001_USER_ID: [200, {'state': True}],
                                      ACTOR0002_USER_ID: [403, {'msg': 'permission denied'}]}, response.json)

                    query_string = {'api-key': ACTOR0002_KEY,
                                    'actors': json.dumps([ACTOR0001_USER_ID, ACTOR0002_USER_ID])}
                    response = self.app_test.get('/api/getState', query_string=query_string, follow_redirects=True)
                    self.assertEqual(200, response.status_code)
                    self.assertEqual({ACTOR0001_USER_ID: [403, {'msg': 'permission denied'}],
                                      ACTOR0002_USER_ID: [200, {'state': True}]}, response.json)

            with mock_datetime_now(TS_12_30_02, datetime):
                query_string = {'api-key': ACTOR0001_KEY,
                                'actors': json.dumps([ACTOR0001_USER_ID, ACTOR0002_USER_ID])}
                response = self.app_test.get('/api/getState', query_string=query_string, follow_redirects=True)
                self.assertEqual(200, response.status_code)
                self.assertEqual({ACTOR0001_USER_ID: [200, {'state': False}],
                                  ACTOR0002_USER_ID: [403, {'msg': 'permission denied'}]}, response.json)

                query_string = {'api-key': ACTOR0002_KEY,
                                'actors': json.dumps([ACTOR0001_USER_ID, ACTOR0002_USER_ID])}
                response = self.app_test.get('/api/getState', query_string=query_string, follow_redirects=True)
                self.assertEqual(200, response.status_code)
                self.assertEqual({ACTOR0001_USER_ID: [403, {'msg': 'permission denied'}],
                                  ACTOR0002_USER_ID: [200, {'state': False}]}, response.json)

            with mock_datetime_now(TS_12_30_11, datetime):
                query_string = {'api-key': ACTOR0001_KEY,
                                'actors': json.dumps([ACTOR0001_USER_ID, ACTOR0002_USER_ID])}
                response = self.app_test.get('/api/getState', query_string=query_string, follow_redirects=True)
                self.assertEqual(200, response.status_code)
                self.assertEqual({ACTOR0001_USER_ID: [200, {'state': False}],
                                  ACTOR0002_USER_ID: [403, {'msg': 'permission denied'}]}, response.json)

                query_string = {'api-key': ACTOR0002_KEY,
                                'actors': json.dumps([ACTOR0001_USER_ID, ACTOR0002_USER_ID])}
                response = self.app_test.get('/api/getState', query_string=query_string, follow_redirects=True)
                self.assertEqual(200, response.status_code)
                self.assertEqual({ACTOR0001_USER_ID: [403, {'msg': 'permission denied'}],
                                  ACTOR0002_USER_ID: [200, {'state': True}]}, response.json)

            # get state for a wrong actor id
            query_string = {'api-key': ACTOR0001_KEY,
                            'actors': json.dumps(['wxyz'])}
            response = self.app_test.get('/api/getState', query_string=query_string, follow_redirects=True)
            self.assertEqual(200, response.status_code)
            self.assertEqual({'wxyz': [401, {'msg': 'malformed uuid string'}]}, response.json)

            # get state for an actor with no entries in state table
            query_string = {'api-key': ACTOR0003_KEY,
                            'actors': json.dumps([ACTOR0003_USER_ID])}
            response = self.app_test.get('/api/getState', query_string=query_string, follow_redirects=True)
            self.assertEqual(200, response.status_code)
            self.assertEqual({ACTOR0003_USER_ID: [200, {'state': False}]}, response.json)

            # get initial state for an existing actor id, but with a key that is lacking permission
            query_string = {'api-key': ACTOR0003_KEY,
                            'actors': json.dumps([ACTOR0001_USER_ID])}
            response = self.app_test.get('/api/getState', query_string=query_string, follow_redirects=True)
            self.assertEqual(200, response.status_code)
            self.assertEqual({ACTOR0001_USER_ID: [403, {'msg': 'permission denied'}]}, response.json)

            # this is an unknown key
            query_string = {'api-key': '9999d77d28bf4c53e13719136180dcef2d54c75b37b8a3553339859255731d9d',
                            'actors': json.dumps([ACTOR0001_USER_ID])}
            response = self.app_test.get('/api/getState', query_string=query_string, follow_redirects=True)
            self.assertEqual(403, response.status_code)
            self.assertEqual({'msg': 'access denied'}, response.json)

    # def test_api_generate_api_key(self):
    #     return
    #     with mock_datetime_now(TS_12_30_00, datetime):
    #         query_string = {'api-key': ADMIN_KEY, 'user-id': 'us0003'}
    #         response = self.app_test.get('/api/createApiKey', query_string=query_string, follow_redirects=True)
    #         response_json = dict(response.json)
    #         api_key = response_json.pop('api-key')
    #         self.assertEqual({'msg': 'api key generated'}, response_json)
    #         self.assertEqual(200, response.status_code)
    #         self.assertEqual(64, len(api_key))
    #
    #         query_string = {'api-key': ADMIN_KEY, 'user-id': 'us0002'}
    #         response2 = self.app_test.get('/api/createApiKey', query_string=query_string, follow_redirects=True)
    #         response2_json = dict(response2.json)
    #         api_key2 = response2_json.pop('api-key')
    #         self.assertEqual({'msg': 'api key generated'}, response2_json)
    #         self.assertEqual(200, response2.status_code)
    #         self.assertEqual(64, len(api_key2))
    #
    #         self.assertNotEqual(api_key, api_key2)
