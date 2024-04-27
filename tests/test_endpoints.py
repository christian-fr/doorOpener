import datetime
import json
import secrets
import uuid

from unittest import TestCase
from sqlalchemy import select

from app.app import create_app, db
from app.api.routes import response_permission_error, response_input_error, response_success
from app.models.user import User, Role
from app.models.scope import Scope, Mode
from app.models.valid import Valid
from app.util.util import generate_api_key, simple_hash_str

from tests.context.testfixture_config import Config

from tests.test_fns import (USER0002_KEY, ACTOR0001_KEY, ACTOR0002_KEY, TS_11_00_00, TS_12_29_00, TS_12_30_00,
                            TS_12_30_01, TS_12_30_02, TS_12_30_03, TS_12_30_04, TS_12_30_05, TS_12_30_06, TS_12_30_07,
                            TS_12_30_08, TS_12_30_09, TS_12_30_10, TS_12_30_11, TS_12_30_12, set_up_users, set_up_valid,
                            set_up_scope, set_up_state, ACTOR0002_USER_ID, ACTOR0001_USER_ID, ACTOR0003_USER_ID,
                            ACTOR0003_KEY, ADMIN_KEY, USER0006_USER_ID, MAINTENANCE_KEY, TS_12_31_00, USER0001_KEY,
                            USER0001_USER_ID)
from tests.util.mock_datetime import mock_datetime_now

BUILTIN_ADMIN_KEY = None


class TestApiEndpoints(TestCase):
    def setUp(self):
        config = Config.get_cls()
        config.SECRET_KEY = secrets.token_hex()
        self.app = create_app(config_class=config)
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
        for ts in [TS_12_29_00, TS_12_30_00, TS_12_30_01, TS_12_30_02, TS_12_30_02, TS_12_30_03, TS_12_30_04,
                   TS_12_30_05, TS_12_30_06, TS_12_30_07, TS_12_30_08, TS_12_30_09, TS_12_30_10, TS_12_30_11,
                   TS_12_30_12]:
            with mock_datetime_now(ts, datetime):
                query_string = {'api-key': ACTOR0002_KEY, 'actor-id': ACTOR0002_USER_ID}
                response = self.app_test.get('/api/getState', query_string=query_string, follow_redirects=True)
                self.assertEqual(200, response.status_code)
                self.assertEqual({'state': False}, response.json)

        with mock_datetime_now(TS_12_30_01, datetime):
            data = {'api-key': USER0002_KEY, 'actor-id': ACTOR0002_USER_ID}
            response = self.app_test.post('/api/setState', data=data, follow_redirects=True)
            self.assertEqual(200, response.status_code)
            self.assertEqual(response_success().json, response.json)

        for ts in [TS_12_29_00, TS_12_30_00, TS_12_30_12]:
            with mock_datetime_now(ts, datetime):
                query_string = {'api-key': ACTOR0002_KEY, 'actor-id': ACTOR0002_USER_ID}
                response = self.app_test.get('/api/getState', query_string=query_string, follow_redirects=True)
                self.assertEqual(200, response.status_code)
                self.assertEqual({'state': False}, response.json)

        for ts in [TS_12_30_01, TS_12_30_02, TS_12_30_02, TS_12_30_03, TS_12_30_04, TS_12_30_05, TS_12_30_06,
                   TS_12_30_07, TS_12_30_08, TS_12_30_09, TS_12_30_10, TS_12_30_11, ]:
            with mock_datetime_now(ts, datetime):
                query_string = {'api-key': ACTOR0002_KEY, 'actor-id': ACTOR0002_USER_ID}
                response = self.app_test.get('/api/getState', query_string=query_string, follow_redirects=True)
                self.assertEqual(200, response.status_code)
                self.assertEqual({'state': True}, response.json)

    def test_get_state(self):
        # initially set up state table
        set_up_state(self.app, TS_11_00_00)

        with self.app.app_context():
            for ts in [TS_12_30_02, TS_12_30_11, TS_12_30_12]:
                with mock_datetime_now(ts, datetime):
                    query_string = {'api-key': ACTOR0001_KEY, 'actor-id': ACTOR0001_USER_ID.hex}
                    response = self.app_test.get('/api/getState', query_string=query_string, follow_redirects=True)
                    self.assertEqual(200, response.status_code)
                    self.assertEqual({'state': False}, response.json)

            for ts in [TS_12_30_01, TS_12_30_03, TS_12_30_04, TS_12_30_05, TS_12_30_06, TS_12_30_07, TS_12_30_08,
                       TS_12_30_09, TS_12_30_10]:
                with mock_datetime_now(ts, datetime):
                    query_string = {'api-key': ACTOR0001_KEY, 'actor-id': ACTOR0001_USER_ID.hex}
                    response = self.app_test.get('/api/getState', query_string=query_string, follow_redirects=True)
                    self.assertEqual(200, response.status_code)
                    self.assertEqual({'state': True}, response.json)

            # more than one actor in list
            for ts in [TS_12_29_00, TS_12_30_04]:
                with mock_datetime_now(ts, datetime):
                    query_string = {'api-key': ACTOR0001_KEY, 'actor-id': ACTOR0001_USER_ID}
                    response = self.app_test.get('/api/getState', query_string=query_string, follow_redirects=True)
                    self.assertEqual(200, response.status_code)
                    self.assertEqual({'state': True}, response.json)
                    query_string = {'api-key': ACTOR0001_KEY, 'actor-id': ACTOR0002_USER_ID}
                    response = self.app_test.get('/api/getState', query_string=query_string, follow_redirects=True)
                    self.assertEqual(response_permission_error().status_code, response.status_code)
                    self.assertEqual(response_permission_error().json, response.json)

                    query_string = {'api-key': ACTOR0002_KEY, 'actor-id': ACTOR0001_USER_ID}
                    response = self.app_test.get('/api/getState', query_string=query_string, follow_redirects=True)
                    self.assertEqual(response_permission_error().status_code, response.status_code)
                    self.assertEqual(response_permission_error().json, response.json)
                    query_string = {'api-key': ACTOR0002_KEY, 'actor-id': ACTOR0002_USER_ID}
                    response = self.app_test.get('/api/getState', query_string=query_string, follow_redirects=True)
                    self.assertEqual(200, response.status_code)
                    self.assertEqual({'state': True}, response.json)

            with mock_datetime_now(TS_12_30_02, datetime):
                query_string = {'api-key': ACTOR0001_KEY, 'actor-id': ACTOR0001_USER_ID}
                response = self.app_test.get('/api/getState', query_string=query_string, follow_redirects=True)
                self.assertEqual(200, response.status_code)
                self.assertEqual({'state': False}, response.json)
                query_string = {'api-key': ACTOR0001_KEY, 'actor-id': ACTOR0002_USER_ID}
                response = self.app_test.get('/api/getState', query_string=query_string, follow_redirects=True)
                self.assertEqual(response_permission_error().status_code, response.status_code)
                self.assertEqual(response_permission_error().json, response.json)

                query_string = {'api-key': ACTOR0002_KEY, 'actor-id': ACTOR0001_USER_ID}
                response = self.app_test.get('/api/getState', query_string=query_string, follow_redirects=True)
                self.assertEqual(response_permission_error().status_code, response.status_code)
                self.assertEqual(response_permission_error().json, response.json)
                query_string = {'api-key': ACTOR0002_KEY, 'actor-id': ACTOR0002_USER_ID}
                response = self.app_test.get('/api/getState', query_string=query_string, follow_redirects=True)
                self.assertEqual(200, response.status_code)
                self.assertEqual({'state': False}, response.json)

            with mock_datetime_now(TS_12_30_11, datetime):
                query_string = {'api-key': ACTOR0001_KEY, 'actor-id': ACTOR0001_USER_ID}
                response = self.app_test.get('/api/getState', query_string=query_string, follow_redirects=True)
                self.assertEqual(200, response.status_code)
                self.assertEqual({'state': False}, response.json)
                query_string = {'api-key': ACTOR0001_KEY, 'actor-id': ACTOR0002_USER_ID}
                response = self.app_test.get('/api/getState', query_string=query_string, follow_redirects=True)
                self.assertEqual(response_permission_error().status_code, response.status_code)
                self.assertEqual(response_permission_error().json, response.json)

                query_string = {'api-key': ACTOR0002_KEY, 'actor-id': ACTOR0001_USER_ID}
                response = self.app_test.get('/api/getState', query_string=query_string, follow_redirects=True)
                self.assertEqual(response_permission_error().status_code, response.status_code)
                self.assertEqual(response_permission_error().json, response.json)
                query_string = {'api-key': ACTOR0002_KEY, 'actor-id': ACTOR0002_USER_ID}
                response = self.app_test.get('/api/getState', query_string=query_string, follow_redirects=True)
                self.assertEqual(200, response.status_code)
                self.assertEqual({'state': True}, response.json)

                with mock_datetime_now(TS_12_30_11, datetime):
                    # get state for a wrong actor id
                    query_string = {'api-key': ACTOR0001_KEY, 'actor-id': json.dumps(['wxyz'])}
                    response = self.app_test.get('/api/getState', query_string=query_string, follow_redirects=True)
                    self.assertEqual(response_input_error().status_code, response.status_code)
                    self.assertEqual(response_input_error().json, response.json)

                    # get state for an actor with no entries in state table
                    query_string = {'api-key': ACTOR0003_KEY, 'actor-id': ACTOR0003_USER_ID}
                    response = self.app_test.get('/api/getState', query_string=query_string, follow_redirects=True)
                    self.assertEqual(200, response.status_code)
                    self.assertEqual({'state': False}, response.json)

                    # get initial state for an existing actor id, but with a key that is lacking permission
                    query_string = {'api-key': ACTOR0003_KEY, 'actor-id': ACTOR0001_USER_ID}
                    response = self.app_test.get('/api/getState', query_string=query_string, follow_redirects=True)
                    self.assertEqual(response_permission_error().status_code, response.status_code)
                    self.assertEqual(response_permission_error().json, response.json)

                # get state with actor id that is currently valid
                with mock_datetime_now(TS_12_30_11, datetime):
                    query_string = {'api-key': ACTOR0003_KEY, 'actor-id': ACTOR0003_USER_ID}
                    response = self.app_test.get('/api/getState', query_string=query_string, follow_redirects=True)
                    self.assertEqual(200, response.status_code)
                    self.assertEqual({'state': False}, response.json)

            # get state with actor id that is currently invalid
            with mock_datetime_now(TS_12_30_12, datetime):
                query_string = {'api-key': ACTOR0003_KEY, 'actor-id': ACTOR0003_USER_ID}
                response = self.app_test.get('/api/getState', query_string=query_string, follow_redirects=True)
                self.assertEqual(response_permission_error().status_code, response.status_code)
                self.assertEqual(response_permission_error().json, response.json)

    def test_get_state02(self):
        # initially set up state table
        set_up_state(self.app, TS_11_00_00)

        with self.app.app_context():
            with mock_datetime_now(TS_12_30_11, datetime):
                # this is an unknown key
                query_string = {'api-key': '9999d77d28bf4c53e13719136180dcef2d54c75b37b8a3553339859255731d9d',
                                'actor-id': ACTOR0001_USER_ID}
                response = self.app_test.get('/api/getState', query_string=query_string, follow_redirects=True)
                self.assertEqual(response_permission_error().status_code, response.status_code)
                self.assertEqual(response_permission_error().json, response.json)

    def test_add_user_error(self):
        with (self.app.app_context()):
            query_string = {'api-key': BUILTIN_ADMIN_KEY, 'name': 'new User', 'role': 'unknown_role'}
            response = self.app_test.get('/api/addUser', query_string=query_string, follow_redirects=True)
            self.assertEqual(404, response.status_code)

    def test_add_user(self):
        with (self.app.app_context()):
            properties = [User.id, User.api_key, User.name, User.role]
            query = select(*properties)
            user_data_ex_ante = {user_data[0]: user_data[1:] for user_data in db.session.execute(query)}

            query_string = {'api-key': BUILTIN_ADMIN_KEY, 'name': 'new User', 'role': Role.user.name}
            response = self.app_test.get('/api/addUser', query_string=query_string, follow_redirects=True)
            response_json = response.json.copy()
            self.assertEqual(200, response.status_code)

            user_id = response_json['id']
            user_api_key = response_json['api_key']
            user_password = response_json['password']
            self.assertTrue(isinstance(uuid.UUID(user_id), uuid.UUID))
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

    def test_regenerate_api_key(self):
        with (self.app.app_context()):
            properties = [User.id, User.api_key, User.name, User.role]
            query = select(*properties)
            user_data_ex_ante = {user_data[0]: user_data[1:] for user_data in db.session.execute(query)}
            old_api_key_hashed = user_data_ex_ante[USER0001_USER_ID][0]

            query_string = {'api-key': USER0001_KEY}
            response = self.app_test.get('/api/regenerateApiKey', query_string=query_string, follow_redirects=True)
            response_json = response.json.copy()
            new_api_key = response_json['api_key']
            self.assertEqual(200, response.status_code)

            self.assertEqual(len(generate_api_key()), len(new_api_key))

            query = select(*properties)
            user_data_ex_post = {user_data[0]: user_data[1:] for user_data in db.session.execute(query)}
            new_api_key_hashed = user_data_ex_post[USER0001_USER_ID][0]

            self.assertNotEqual(old_api_key_hashed, new_api_key_hashed)
            self.assertNotEqual(simple_hash_str(USER0001_KEY), new_api_key_hashed)
            self.assertEqual(simple_hash_str(new_api_key), new_api_key_hashed)

    def test_add_scope(self):
        with (self.app.app_context()):
            properties = [Scope.id, Scope.user_id, Scope.actor_id, Scope.mode]
            query = select(*properties)
            scope_data_ex_ante = {scope_data[0]: scope_data[1:] for scope_data in db.session.execute(query)}

            query_string = {'api-key': BUILTIN_ADMIN_KEY, 'user-id': USER0006_USER_ID, 'actor-id': ACTOR0003_USER_ID,
                            'mode': Mode.write}
            response = self.app_test.get('/api/addScope', query_string=query_string, follow_redirects=True)
            self.assertEqual(200, response.status_code)

            query = select(*properties)
            scope_data_ex_post = {scope_data[0]: scope_data[1:] for scope_data in db.session.execute(query)}

            new_scope_key = set(scope_data_ex_post.keys()).difference(scope_data_ex_ante)
            assert len(new_scope_key) == 1
            new_scope_data = scope_data_ex_post[list(new_scope_key)[0]]
            self.assertEqual(USER0006_USER_ID, new_scope_data[0])
            self.assertEqual(ACTOR0003_USER_ID, new_scope_data[1])
            self.assertEqual(Mode.write, new_scope_data[2])

    def test_add_valid(self):
        with (self.app.app_context()):
            properties = [Valid.id, Valid.user_id, Valid.start, Valid.end]
            query = select(*properties)
            valid_data_ex_ante = {valid_data[0]: valid_data[1:] for valid_data in db.session.execute(query)}

            query_string = {'api-key': BUILTIN_ADMIN_KEY, 'user-id': USER0006_USER_ID, 'start': None,
                            'end': TS_12_30_07}
            response = self.app_test.get('/api/addValid', query_string=query_string, follow_redirects=True)
            self.assertEqual(200, response.status_code)

            query = select(*properties)
            valid_data_ex_post = {valid_data[0]: valid_data[1:] for valid_data in db.session.execute(query)}

            new_valid_key = set(valid_data_ex_post.keys()).difference(valid_data_ex_ante)
            assert len(new_valid_key) == 1
            new_valid_data = valid_data_ex_post[list(new_valid_key)[0]]
            self.assertEqual(USER0006_USER_ID, new_valid_data[0])
            self.assertIsNone(new_valid_data[1])
            self.assertEqual(TS_12_30_07, new_valid_data[2].replace(tzinfo=datetime.timezone.utc))

    def test_new_user_new_actor_new_scope_new_valid(self):
        with (self.app.app_context()):
            with mock_datetime_now(TS_12_29_00, datetime):
                # create user
                query_string = {'api-key': BUILTIN_ADMIN_KEY,
                                'name': 'new User', 'role': Role.user.name}
                response = self.app_test.get('/api/addUser', query_string=query_string, follow_redirects=True)
                response_json = response.json.copy()
                self.assertEqual(200, response.status_code)

                user_id = response_json.pop('id')
                user_api_key = response_json.pop('api_key')

                # create actor
                query_string = {'api-key': BUILTIN_ADMIN_KEY,
                                'name': 'new Actor', 'role': Role.actor.name}
                response2 = self.app_test.get('/api/addUser', query_string=query_string, follow_redirects=True)
                response2_json = response2.json.copy()
                self.assertEqual(200, response2.status_code)

                actor_id = response2_json.pop('id')
                actor_api_key = response2_json.pop('api_key')

                # set scope
                query_string = {'api-key': BUILTIN_ADMIN_KEY, 'user-id': user_id, 'actor-id': actor_id,
                                'mode': Mode.write}
                response3 = self.app_test.get('/api/addScope', query_string=query_string, follow_redirects=True)
                self.assertEqual(200, response3.status_code)

                # set scope
                query_string = {'api-key': BUILTIN_ADMIN_KEY, 'user-id': actor_id, 'actor-id': actor_id,
                                'mode': Mode.read}
                response4 = self.app_test.get('/api/addScope', query_string=query_string, follow_redirects=True)
                self.assertEqual(200, response4.status_code)

                with mock_datetime_now(TS_12_30_01, datetime):
                    query_string = {'api-key': actor_api_key, 'actor-id': actor_id}
                    response = self.app_test.get('/api/getState', query_string=query_string, follow_redirects=True)
                    self.assertEqual(response_permission_error().status_code, response.status_code)
                    self.assertEqual(response_permission_error().json, response.json)

                    query_string = {'api-key': user_api_key, 'actor-id': actor_id}
                    response = self.app_test.get('/api/setState', query_string=query_string, follow_redirects=True)
                    self.assertEqual(response_permission_error().status_code, response.status_code)
                    self.assertEqual(response_permission_error().json, response.json)

                with mock_datetime_now(TS_12_30_02, datetime):
                    # set actor as valid
                    query_string = {'api-key': BUILTIN_ADMIN_KEY, 'user-id': user_id, 'start': None, 'end': None}
                    response = self.app_test.get('/api/addValid', query_string=query_string, follow_redirects=True)
                    self.assertEqual(200, response.status_code)

                    # set user as valid
                    query_string = {'api-key': BUILTIN_ADMIN_KEY, 'user-id': actor_id, 'start': None, 'end': None}
                    response = self.app_test.get('/api/addValid', query_string=query_string, follow_redirects=True)
                    self.assertEqual(200, response.status_code)

                with mock_datetime_now(TS_12_30_02, datetime):
                    # get state for actor
                    query_string = {'api-key': actor_api_key, 'actor-id': actor_id}
                    response = self.app_test.get('/api/getState', query_string=query_string, follow_redirects=True)
                    self.assertEqual(200, response.status_code)
                    self.assertEqual({'state': False}, response.json)

                    # set state for actor
                    query_string = {'api-key': user_api_key, 'actor-id': actor_id}
                    response = self.app_test.get('/api/setState', query_string=query_string, follow_redirects=True)
                    self.assertEqual(200, response.status_code)

                    # get state for actor
                    query_string = {'api-key': actor_api_key, 'actor-id': actor_id}
                    response = self.app_test.get('/api/getState', query_string=query_string, follow_redirects=True)
                    self.assertEqual(200, response.status_code)
                    self.assertEqual({'state': True}, response.json)

                with mock_datetime_now(TS_12_30_01, datetime):
                    query_string = {'api-key': actor_api_key, 'actor-id': actor_id}
                    response5 = self.app_test.get('/api/getState', query_string=query_string, follow_redirects=True)
                    self.assertEqual(200, response5.status_code)
                    self.assertEqual({'state': False}, response5.json)

                with mock_datetime_now(TS_12_30_03, datetime):
                    query_string = {'api-key': actor_api_key, 'actor-id': actor_id}
                    response5 = self.app_test.get('/api/getState', query_string=query_string, follow_redirects=True)
                    self.assertEqual(200, response5.status_code)
                    self.assertEqual({'state': True}, response5.json)

    def test_actor_health_check(self):
        with (self.app.app_context()):
            with mock_datetime_now(TS_12_30_00, datetime):
                # check health of ACTOR0001
                query_string = {'api-key': MAINTENANCE_KEY, 'actor-id': ACTOR0001_USER_ID, 'timeout': 10}
                response = self.app_test.get('/api/actorHealth', query_string=query_string, follow_redirects=True)
                response_json = response.json.copy()
                self.assertEqual(200, response.status_code)
                self.assertEqual({'health': False}, response_json)

            with mock_datetime_now(TS_12_30_01, datetime):
                query_string = {'api-key': ACTOR0001_KEY, 'actor-id': ACTOR0001_USER_ID}
                response = self.app_test.get('/api/getState', query_string=query_string, follow_redirects=True)
                response_json = response.json.copy()
                self.assertEqual(200, response.status_code)
                self.assertEqual({'state': False}, response_json)

                # check health of ACTOR0001
                query_string = {'api-key': MAINTENANCE_KEY, 'actor-id': ACTOR0001_USER_ID, 'timeout': 10}
                response = self.app_test.get('/api/actorHealth', query_string=query_string, follow_redirects=True)
                response_json = response.json.copy()
                self.assertEqual(200, response.status_code)
                self.assertEqual({'health': True}, response_json)

            with mock_datetime_now(TS_12_30_10, datetime):
                # check health of ACTOR0001
                query_string = {'api-key': MAINTENANCE_KEY, 'actor-id': ACTOR0001_USER_ID, 'timeout': 10}
                response = self.app_test.get('/api/actorHealth', query_string=query_string, follow_redirects=True)
                response_json = response.json.copy()
                self.assertEqual(200, response.status_code)
                self.assertEqual({'health': True}, response_json)

            with mock_datetime_now(TS_12_30_11, datetime):
                # check health of ACTOR0001
                query_string = {'api-key': MAINTENANCE_KEY, 'actor-id': ACTOR0001_USER_ID, 'timeout': 10}
                response = self.app_test.get('/api/actorHealth', query_string=query_string, follow_redirects=True)
                response_json = response.json.copy()
                self.assertEqual(200, response.status_code)
                self.assertEqual({'health': True}, response_json)

            with mock_datetime_now(TS_12_30_12, datetime):
                # check health of ACTOR0001
                query_string = {'api-key': MAINTENANCE_KEY, 'actor-id': ACTOR0001_USER_ID, 'timeout': 10}
                response = self.app_test.get('/api/actorHealth', query_string=query_string, follow_redirects=True)
                response_json = response.json.copy()
                self.assertEqual(200, response.status_code)
                self.assertEqual({'health': False}, response_json)

            with mock_datetime_now(TS_12_31_00, datetime):
                # check health of ACTOR0001
                query_string = {'api-key': MAINTENANCE_KEY, 'actor-id': ACTOR0001_USER_ID, 'timeout': 10}
                response = self.app_test.get('/api/actorHealth', query_string=query_string, follow_redirects=True)
                response_json = response.json.copy()
                self.assertEqual(200, response.status_code)
                self.assertEqual({'health': False}, response_json)

            with mock_datetime_now(TS_12_31_00, datetime):
                # check health of ACTOR0001
                query_string = {'api-key': MAINTENANCE_KEY, 'actor-id': ACTOR0001_USER_ID, 'timeout': 60}
                response = self.app_test.get('/api/actorHealth', query_string=query_string, follow_redirects=True)
                response_json = response.json.copy()
                self.assertEqual(200, response.status_code)
                self.assertEqual({'health': True}, response_json)

                # check health of ACTOR0001
                query_string = {'api-key': MAINTENANCE_KEY, 'actor-id': ACTOR0001_USER_ID, 'timeout': 58}
                response = self.app_test.get('/api/actorHealth', query_string=query_string, follow_redirects=True)
                response_json = response.json.copy()
                self.assertEqual(200, response.status_code)
                self.assertEqual({'health': False}, response_json)
