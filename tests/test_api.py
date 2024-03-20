import datetime
import json
from pathlib import Path
from unittest import TestCase
import os

from app import create_app, db

from tests.context.testfixture_config import Config

from tests.test_fns import (USER0001_KEY, USER0002_KEY, USER0003_KEY, ACTOR0001_KEY, ACTOR0002_KEY, ADMIN_KEY,
                            TS_11_00_00,
                            TS_12_29_00, TS_12_30_00, TS_12_30_01, TS_12_30_02, TS_12_30_03, TS_12_30_04, TS_12_30_05,
                            TS_12_30_06, TS_12_30_07, TS_12_30_08, TS_12_30_09, TS_12_30_10, TS_12_30_11, TS_12_30_12,
                            TS_12_31_00, TS_16_00_00, set_up_users, set_up_valid, set_up_scope, set_up_state,
                            ACTOR0002_USER_ID, ACTOR0001_USER_ID, ACTOR0003_USER_ID, ACTOR0003_KEY)
from tests.util.mock_datetime import mock_datetime_now


class TestApiEndpoints(TestCase):
    # @classmethod
    # def setUpClass(cls):
    #     return
    #     cls.app = create_app(config_class=Config)
    #     with cls.app.app_context():
    #         db.drop_all()
    #         db.create_all()
    #         db.session.commit()
    #     cls.app_test = cls.app.test_client()

    # @classmethod
    # def tearDownClass(cls):
    #     return
    #     with cls.app.app_context():
    #         db.drop_all()
    #
    #     if 'SQLALCHEMY_DATABASE_URI' in cls.app.config:
    #         db_path = cls.app.config['SQLALCHEMY_DATABASE_URI']
    #         if db_path.startswith('sqlite:///') and db_path.endswith('test.sqlite'):
    #             db_path_file = Path(db_path[len('sqlite:///'):])
    #             if db_path_file.exists():
    #                 os.remove(db_path_file)

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
                self.assertEqual((200, {ACTOR0002_USER_ID: (200, {'msg': 'false'})}),
                                 get_state([ACTOR0002_USER_ID], ACTOR0002_KEY))
        with mock_datetime_now(TS_12_30_01, datetime):
            self.assertEqual((200, {ACTOR0002_USER_ID: (200, {'msg': 'success'})}),
                             set_state([ACTOR0002_USER_ID], USER0002_KEY))

        for ts in [TS_12_29_00, TS_12_30_00, TS_12_30_12]:
            with mock_datetime_now(ts, datetime):
                self.assertEqual((200, {ACTOR0002_USER_ID: (200, {'msg': 'false'})}),
                                 get_state([ACTOR0002_USER_ID], ACTOR0002_KEY))
        for ts in [TS_12_30_01, TS_12_30_02, TS_12_30_02, TS_12_30_03, TS_12_30_04, TS_12_30_05, TS_12_30_06,
                   TS_12_30_07, TS_12_30_08, TS_12_30_09, TS_12_30_10, TS_12_30_11, ]:
            with mock_datetime_now(ts, datetime):
                a = (200, {ACTOR0002_USER_ID: (200, {'msg': 'true'})}) == get_state([ACTOR0002_USER_ID],
                                                                                    ACTOR0002_KEY)
                self.assertEqual((200, {ACTOR0002_USER_ID: (200, {'msg': 'true'})}),
                                 get_state([ACTOR0002_USER_ID], ACTOR0002_KEY))

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


                    self.assertEqual((200, {'1dad0dc3-f862-4b41-9608-2ee1fa3050c2': (403, {'msg': 'permission denied'}),
                                            'd526569c-4743-4d3e-a742-128051f63f72': (200, {'msg': 'true'})}),
                                     get_state([ACTOR0001_USER_ID, ACTOR0002_USER_ID], ACTOR0002_KEY))

            with mock_datetime_now(TS_12_30_02, datetime):
                self.assertEqual((200, {'1dad0dc3-f862-4b41-9608-2ee1fa3050c2': (200, {'msg': 'false'}),
                                        'd526569c-4743-4d3e-a742-128051f63f72': (403, {'msg': 'permission denied'})}),
                                 get_state([ACTOR0001_USER_ID, ACTOR0002_USER_ID], ACTOR0001_KEY))
                self.assertEqual((200, {'1dad0dc3-f862-4b41-9608-2ee1fa3050c2': (403, {'msg': 'permission denied'}),
                                        'd526569c-4743-4d3e-a742-128051f63f72': (200, {'msg': 'false'})}),
                                 get_state([ACTOR0001_USER_ID, ACTOR0002_USER_ID], ACTOR0002_KEY))

            with mock_datetime_now(TS_12_30_11, datetime):
                self.assertEqual((200, {'1dad0dc3-f862-4b41-9608-2ee1fa3050c2': (200, {'msg': 'false'}),
                                        'd526569c-4743-4d3e-a742-128051f63f72': (403, {'msg': 'permission denied'})}),
                                 get_state([ACTOR0001_USER_ID, ACTOR0002_USER_ID], ACTOR0001_KEY))
                self.assertEqual((200, {'1dad0dc3-f862-4b41-9608-2ee1fa3050c2': (403, {'msg': 'permission denied'}),
                                        'd526569c-4743-4d3e-a742-128051f63f72': (200, {'msg': 'true'})}),
                                 get_state([ACTOR0001_USER_ID, ACTOR0002_USER_ID], ACTOR0002_KEY))

            # get state for a wrong actor id
            self.assertEqual((200, {'wxyz': (401, {'msg': 'malformed uuid string'})}),
                             get_state(['wxyz'], ACTOR0001_KEY))

            # get state for an actor with no entries in state table
            self.assertEqual((200, {'df809f8d-7689-439c-8dc8-d73d1d49e562': (200, {'msg': 'false'})}),
                             get_state([ACTOR0003_USER_ID], ACTOR0003_KEY))

            # get initial state for an existing actor id, but with a key that is lacking permission
            self.assertEqual((200, {ACTOR0001_USER_ID: (403, {'msg': 'permission denied'})}),
                             get_state([ACTOR0001_USER_ID], ACTOR0003_KEY))

            # this is an unknown key
            self.assertEqual((403, {'msg': 'access denied'}),
                             get_state([ACTOR0001_USER_ID],
                                       '9999d77d28bf4c53e13719136180dcef2d54c75b37b8a3553339859255731d9d'))

    def test_api_generate_api_key(self):
        with mock_datetime_now(TS_12_30_00, datetime):
            query_string = {'api-key': ADMIN_KEY, 'user-id': 'us0003'}
            response = self.app_test.get('/api/createApiKey', query_string=query_string, follow_redirects=True)
            response_json = dict(response.json)
            api_key = response_json.pop('api-key')
            self.assertEqual({'msg': 'api key generated'}, response_json)
            self.assertEqual(200, response.status_code)
            self.assertEqual(64, len(api_key))

            query_string = {'api-key': ADMIN_KEY, 'user-id': 'us0002'}
            response2 = self.app_test.get('/api/createApiKey', query_string=query_string, follow_redirects=True)
            response2_json = dict(response2.json)
            api_key2 = response2_json.pop('api-key')
            self.assertEqual({'msg': 'api key generated'}, response2_json)
            self.assertEqual(200, response2.status_code)
            self.assertEqual(64, len(api_key2))

            self.assertNotEqual(api_key, api_key2)
