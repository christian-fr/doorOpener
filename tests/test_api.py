import datetime
import uuid
from pathlib import Path
from unittest import TestCase
import tempfile
import os

from app import create_app, db

from app.models.scope import Scope
from app.models.state import State
from app.models.valid import Valid
from app.models.users import Users, Role

from tests.context.test_config import Config

from tests.test_fns import (USER0001_KEY, USER0002_KEY, USER0003_KEY, ACTOR0001_KEY, ACTOR0002_KEY, ADMIN_KEY, TS_11_00_00,
                            TS_12_29_00, TS_12_30_00, TS_12_30_01, TS_12_30_02, TS_12_30_03, TS_12_30_04, TS_12_30_05,
                            TS_12_30_06, TS_12_30_07, TS_12_30_08, TS_12_30_09, TS_12_30_10, TS_12_30_11, TS_12_30_12,
                            TS_12_31_00, TS_16_00_00, set_up_testcase)
from tests.util.mock_datetime import mock_datetime_now


class TestApi(TestCase):

    @classmethod
    def setUpClass(cls):
        cls.app = create_app(config_class=Config)
        with cls.app.app_context():
            db.drop_all()
            db.create_all()
            db.session.commit()
        cls.app_test = cls.app.test_client()
        set_up_testcase(cls.app)

    @classmethod
    def tearDownClass(cls):
        with cls.app.app_context():
            db.drop_all()

        if 'SQLALCHEMY_DATABASE_URI' in cls.app.config:
            db_path = cls.app.config['SQLALCHEMY_DATABASE_URI']
            if db_path.startswith('sqlite:///') and db_path.endswith('test.sqlite'):
                db_path_file = Path(db_path[len('sqlite:///'):])
                if db_path_file.exists():
                    os.remove(db_path_file)
        if 'TEMP_DIR' in cls.app.config:
            temp_dir = cls.app.config['TEMP_DIR']
            if isinstance(temp_dir, tempfile.TemporaryDirectory):
                temp_dir.cleanup()

    def test_api(self):
        # self.create_users(self)
        self.api_get_state01(self)

    @staticmethod
    def api_get_state01(test_case: TestCase):
        with mock_datetime_now(TS_12_30_00, datetime):
            query_string = {'api-key': ACTOR0001_KEY, 'actors': '["ac0001"]'}
            response = test_case.app_test.get('/api/getDoorState', query_string=query_string, follow_redirects=True)

            test_case.assertEqual({'ac0001': [200, False]}, response.json)
            test_case.assertEqual(200, response.status_code)

    def test_api_set_state01(self):
        with mock_datetime_now(TS_12_30_00, datetime):
            query_string = {'api-key': ACTOR0001_KEY, 'actors': '["ac0001"]'}
            response = self.app_test.get('/api/getDoorState', query_string=query_string, follow_redirects=True)

            self.assertEqual({'ac0001': [200, False]}, response.json)
            self.assertEqual(200, response.status_code)

        with mock_datetime_now(TS_12_30_01, datetime):
            query_string = {'api-key': USER0001_KEY, 'actors': '["ac0001"]'}
            response = self.app_test.get('/api/setDoorState', query_string=query_string, follow_redirects=True)

            self.assertEqual({'ac0001': 200}, response.json)
            self.assertEqual(200, response.status_code)

        with mock_datetime_now(TS_12_30_02, datetime):
            query_string = {'api-key': ACTOR0001_KEY, 'actors': '["ac0001"]'}
            response = self.app_test.get('/api/getDoorState', query_string=query_string, follow_redirects=True)

            self.assertEqual({'ac0001': [200, True]}, response.json)
            self.assertEqual(200, response.status_code)

        with mock_datetime_now(TS_12_30_05, datetime):
            query_string = {'api-key': ACTOR0001_KEY, 'actors': '["ac0001"]'}
            response = self.app_test.get('/api/getDoorState', query_string=query_string, follow_redirects=True)

            self.assertEqual({'ac0001': [200, True]}, response.json)
            self.assertEqual(200, response.status_code)

        with mock_datetime_now(TS_12_30_06, datetime):
            query_string = {'api-key': ACTOR0001_KEY, 'actors': '["ac0001"]'}
            response = self.app_test.get('/api/getDoorState', query_string=query_string, follow_redirects=True)

            self.assertEqual({'ac0001': [200, False]}, response.json)
            self.assertEqual(200, response.status_code)

    def test_api_create_user(self):
        with mock_datetime_now(TS_12_30_00, datetime):
            query_string = {'api-key': ADMIN_KEY, 'user-id': 'testUser', 'name': 'a test user', 'role': Role.USER.name}
            response = self.app_test.get('/api/createUser', query_string=query_string, follow_redirects=True)
            self.assertEqual({'msg': 'user created', 'user-id': 'testUser'}, response.json)
            self.assertEqual(200, response.status_code)

    def test_api_set_permissions(self):
        query_string = {'api-key': ADMIN_KEY, 'user-id': 'us0002', 'actor-id': 'ac0001', 'mode': 'w'}
        response = self.app_test.get('/api/setPermissions', query_string=query_string, follow_redirects=True)
        response_json = response.json.copy()
        permission_id = response_json.pop('permission-id')
        self.assertEqual({'msg': 'permission modified'}, response_json)
        self.assertEqual(32, len(permission_id))

    def test_api_list_api_keys(self):
        query_string = {'api-key': ADMIN_KEY}
        response = self.app_test.get('/api/listApiKeys', query_string=query_string, follow_redirects=True)
        self.assertEqual({'052b39', '781bd7', '8c267d', '9a9893', 'f160e3'}, set(response.json['api-keys-truncated']))
        self.assertEqual(200, response.status_code)

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
