import datetime
import os
import tempfile
import unittest.mock
import uuid
from pathlib import Path
from unittest import TestCase

import flask

from app import create_app, db, Users, Valid, State
from app.models.scope import Mode, Scope
from app.models.users import Role
from app.util.util import hash_salt_pw, check_pw, simple_hash
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

ACTOR0001_USER_ID = '1dad0dc3-f862-4b41-9608-2ee1fa3050c2'
ACTOR0001_KEY = '9a9893b036fd1708c518467a203de7405184feff1c2eb315ee8099cd8fedab58'
ACTOR0001_KEY_HASH = '47c9509b5ce3dc09e638fbae27075850860870c2118a653e2382e773f59a8b36'

ACTOR0002_USER_ID = 'd526569c-4743-4d3e-a742-128051f63f72'
ACTOR0002_KEY = 'f160e336939ee5b8ed3206962c488fc5be3f6e35a3ca92fc170e80657958bda3'
ACTOR0002_KEY_HASH = 'f753132d9a2f3f33df3144c14572f26cc9b818fcbd4791ab3aa755e006e00c12'

USER0001_USER_ID = '1f4a6f9c-af4a-4a32-976d-e86a1487ec43'
USER0001_KEY = '052b3945b6913a005c74c52d0a2c48cfc7c10207db775d51950a21bc12dcc472'
USER0001_KEY_HASH = 'bd0a725364a81e9a4eb240ffe937e22cdc16f3af816f261d9c8954db45651347'
USER0001_PASSWORD = 'SonneMondUndSterne'
USER0001_PW_HASH = b'$2b$12$OIsDWfLOPdNpsXUuAUuukOgE2PBByP/CJzYY4kbmWoIYuYtwoZaXK'

USER0002_USER_ID = '72031898-24eb-46d4-b4de-40355517ef8e'
USER0002_KEY = '781bd77d28bf4c53e13719136180dcef2d54c75b37b8a3553339859255731d9d'
USER0002_KEY_HASH = '1315299744412e5372ffda0f2dc9243718dcf427dca3f5f9e5b011d91704a716'
USER0002_PASSWORD = 'OneAndOneAndOneIsThree'
USER0002_PW_HASH = b'$2b$12$hVZw4gxhkoIMtbjCZ1bWZ.Hv7GEIV6h3kO6mFUCZSfuZ/lEpFBB7i'

USER0003_USER_ID = 'd8977529-31bd-4f3e-b24c-91f31d962487'
USER0003_KEY = '8c267d03891a23661ec3e89dbed546297cb86bae05d4767ff01cc0b1616d3499'
USER0003_KEY_HASH = '9abeadff6fb0f6da5f52c1722f75763c620e8fa469a22bb665a2e1b655dd76dd'
USER0003_PASSWORD = 'RocknRoll'
USER0003_PW_HASH = b'$2b$12$OIsDWfLOPdNpsXUuAUuukOgE2PBByP/CJzYY4kbmWoIYuYtwoZaXK'

USER0004_USER_ID = 'c100c404-4f65-4a23-b5d9-0979dad67fec'
USER0004_KEY = '58a0d55f80247f4b554dcae9ad274b8e96105519cd87a344bb017f42cc762b86'
USER0004_KEY_HASH = 'bbfaa8566e916c7a8e9df537a2ef27c170da8f2cedcd34eebf600cd4cdd2096f'
USER0004_PASSWORD = 'AlleMeineEntchen'
USER0004_PW_HASH = b'$2b$12$QBJzGrzBK5mIucCxHXfITumdGqWWzaT19H/4G7WLiWdO9qoHt9YGu'

USER0005_USER_ID = '17b6909f-565f-4416-a587-3a8791aef0e7'
USER0005_KEY = '961e67183206708d327ae766e6ac34f6ac0c082e0af8763ca8e8d3228496259a'
USER0005_KEY_HASH = '7e3cc041c5dc038fdb8314ccffef9de25786211ad6c4df73ac9f93c3f21624f8'
USER0005_PASSWORD = 'JingleBellsRock'
USER0005_PW_HASH = b'$2b$12$81GAJhj2dPzE92rk5QwrPOKWscn/cdwOknZC8c9PIZbZ2wvZzGr0G'

USER0006_USER_ID = '9f1b6399-f051-44c3-bab3-1a4b8eb81e28'
USER0006_KEY = '535b4e070c23cca91a2044258b2f8cbabe7c58c5fe18f7a88d13c85a3c8db068'
USER0006_KEY_HASH = '0dd3fdfceaa2356f91b28f6a3c0be1ef0fe3589dc24e507202e543ae3feb142c'
USER0006_PASSWORD = 'SuesserDieGlockenNieKlingen'
USER0006_PW_HASH = b'$2b$12$zH0fFDodf79ngCEnTyZccOsUYcDvS52gg7N7kv9l/qAyzfAzZXC4u'

DISABLED_USER_ID = '4c86f252-7d14-4776-a9a7-2e85e23b4f69'
DISABLED_KEY = '9c1e953d91c1bf590dcb2a6011d8f0370fd0df12baea0adfd536175596f10d43'
DISABLED_KEY_HASH = '22ac7e4d3dc2812f231c761fca8c63f7b34ce2546034878c2b69cc077747546a'
DISABLED_PASSWORD = 'KeinSchoenerLand'
DISABLED_PW_HASH = b'$2b$12$7KSsl6T7igXPMUGYjxGQXOl1QKa/ax6KREZkmpdTkQoJWIyhrhBp6'

ADMIN_USER_ID = '32546de6-7c94-41b8-812b-4f5786b71e1c'
ADMIN_KEY = '98cfefb9d2c1477b3d98ebd19ec7a69bc0f82ce81a1ee88fcbdfe07a7681a829'
ADMIN_KEY_HASH = '6fe5298db99863db6267e9f06a2f22f425d870eb28b7b54313da1b048d6c1b4d'
ADMIN_PASSWORD = 'SuperSudo'
ADMIN_PW_HASH = b'$2b$12$Ic5poQoe.y9JW./XLGtXO.gBugpsfFVrRfHf5.6c4As9JYvVaHe3e'

for key, hash in [(USER0001_KEY, USER0001_KEY_HASH),
                  (USER0002_KEY, USER0002_KEY_HASH),
                  (USER0003_KEY, USER0003_KEY_HASH),
                  (USER0004_KEY, USER0004_KEY_HASH),
                  (USER0005_KEY, USER0005_KEY_HASH),
                  (USER0006_KEY, USER0006_KEY_HASH),
                  (DISABLED_KEY, DISABLED_KEY_HASH),
                  (ADMIN_KEY, ADMIN_KEY_HASH)]:
    assert simple_hash(key.encode('utf-8')).hex() == hash

VALID01_ID = 'c5026b88-7782-4dc3-b930-3c8121da7644'
VALID02_ID = '5a15b116-6f48-4186-9c5b-b8240d5a8ff3'
VALID03_ID = '02ed3c6b-a9aa-4207-8f42-c3ec57359322'
VALID04_ID = 'd04e218a-64b0-432c-aaf7-e4dfac8b635a'
VALID05_ID = '3f68de07-f81f-4b10-a28d-2c235d1d72de'
VALID06_ID = '0c59b73c-bd39-48bd-9d75-48d559202cde'
VALID07_ID = '7cf580c4-22a1-4b9e-b3c1-08bc3421f18e'
VALID08_ID = '5ef12355-55e4-4eb9-849d-92d3a3e1a2ef'

SCOPE01_ID = '6af8022f-3843-4f6d-aedf-82054bef1425'
SCOPE02_ID = 'ad178135-5de5-4e8f-8c02-662a831f5ab2'
SCOPE03_ID = 'dbb5aa11-6898-4b0e-bf7a-71beeba86e4f'
SCOPE04_ID = 'bd7cca24-8658-4724-abc9-481355a5442e'
SCOPE05_ID = 'e1f760d0-23d0-4d31-aa08-c72b3e550a80'
SCOPE06_ID = '3df49528-24c2-4397-b346-65e56e7e1f34'

STATE01_ID = '57441403-e8f3-438c-999d-6264079eb95a'
STATE02_ID = '1b785226-a486-4e1b-b2c9-512d7babdc38'


def date_to_str(date: datetime.datetime) -> str:
    return date.strftime('%Y-%m-%dT%H:%M:%S.%f')


def str_to_date(date: str) -> datetime.datetime:
    return datetime.datetime.strptime(date, '%Y-%m-%dT%H:%M:%S.%f')


TS_12_29_00str = date_to_str(TS_12_29_00)
TS_12_30_06str = date_to_str(TS_12_30_06)


def set_up_users(app: flask.app.Flask, timestamp: datetime.datetime) -> None:
    with mock_datetime_now(timestamp, datetime):
        user0001_data = {'id': uuid.UUID(USER0001_USER_ID), 'name': 'USER0001', 'email': None,
                         'password': USER0001_PW_HASH, 'api_key': USER0001_KEY_HASH, 'role': Role.user, }
        user0002_data = {'id': uuid.UUID(USER0002_USER_ID), 'name': 'USER0002', 'email': None,
                         'password': USER0002_PW_HASH, 'api_key': USER0002_KEY_HASH, 'role': Role.user, }
        user0003_data = {'id': uuid.UUID(USER0003_USER_ID), 'name': 'USER0003', 'email': None,
                         'password': USER0003_PW_HASH, 'api_key': USER0003_KEY_HASH, 'role': Role.user, }
        user0004_data = {'id': uuid.UUID(USER0004_USER_ID), 'name': 'USER0004', 'email': None,
                         'password': USER0004_PW_HASH, 'api_key': USER0004_KEY_HASH, 'role': Role.user, }
        user0005_data = {'id': uuid.UUID(USER0005_USER_ID), 'name': 'USER0005', 'email': None,
                         'password': USER0005_PW_HASH, 'api_key': USER0005_KEY_HASH, 'role': Role.user, }
        user0006_data = {'id': uuid.UUID(USER0006_USER_ID), 'name': 'USER0006', 'email': None,
                         'password': USER0006_PW_HASH, 'api_key': USER0006_KEY_HASH, 'role': Role.user, }
        actor0001_data = {'id': uuid.UUID(ACTOR0001_USER_ID), 'name': 'ACTOR1', 'email': None,
                          'password': None, 'api_key': ACTOR0001_KEY_HASH, 'role': Role.actor, }
        actor0002_data = {'id': uuid.UUID(ACTOR0002_USER_ID), 'name': 'ACTOR2', 'email': None,
                          'password': None, 'api_key': ACTOR0002_KEY_HASH, 'role': Role.actor, }
        disabled_data = {'id': uuid.UUID(DISABLED_USER_ID), 'name': 'DISABLED0001', 'email': None,
                         'password': DISABLED_PW_HASH, 'api_key': DISABLED_KEY_HASH, 'role': Role.deactivated, }
        admin_data = {'id': uuid.UUID(ADMIN_USER_ID), 'name': 'ADMIN', 'email': None,
                      'password': ADMIN_PW_HASH, 'api_key': ADMIN_KEY_HASH, 'role': Role.admin, }

        data_list = [user0001_data, user0002_data, user0003_data, user0004_data, user0005_data, user0006_data,
                     actor0001_data, actor0002_data, disabled_data, admin_data]
        created_updated_dict = {'created_at': datetime.datetime.now(), 'updated_at': datetime.datetime.now()}

        user_list = [Users(**data, **created_updated_dict) for data in data_list]
        with app.app_context():
            for user in user_list:
                db.session.add(user)
                db.session.commit()


def set_up_valid(app: flask.app.Flask, timestamp: datetime.datetime) -> None:
    with mock_datetime_now(timestamp, datetime):
        valid01_data = {'id': uuid.UUID(VALID01_ID), 'user_id': uuid.UUID(USER0001_USER_ID), 'start': None, 'end': None}
        valid02_data = {'id': uuid.UUID(VALID02_ID), 'user_id': uuid.UUID(USER0002_USER_ID), 'start': None, 'end': None}
        valid03_data = {'id': uuid.UUID(VALID03_ID), 'user_id': uuid.UUID(USER0003_USER_ID), 'start': None, 'end': None}
        valid04_data = {'id': uuid.UUID(VALID04_ID), 'user_id': uuid.UUID(USER0004_USER_ID), 'start': None,
                        'end': TS_12_29_00}
        valid05_data = {'id': uuid.UUID(VALID05_ID), 'user_id': uuid.UUID(USER0005_USER_ID), 'start': TS_12_29_00,
                        'end': TS_12_30_06}
        valid06_data = {'id': uuid.UUID(VALID06_ID), 'user_id': uuid.UUID(USER0006_USER_ID), 'start': TS_12_30_06,
                        'end': TS_12_29_00}
        valid07_data = {'id': uuid.UUID(VALID07_ID), 'user_id': uuid.UUID(ACTOR0001_USER_ID), 'start': None,
                        'end': None}
        valid08_data = {'id': uuid.UUID(VALID08_ID), 'user_id': uuid.UUID(ACTOR0002_USER_ID), 'start': None,
                        'end': None}

        created_updated_dict = {'created_at': datetime.datetime.now(), 'updated_at': datetime.datetime.now()}

        valid_data_list = [valid01_data, valid02_data, valid03_data, valid04_data, valid05_data, valid06_data,
                           valid07_data, valid08_data]
        valid_list = [Valid(**data, **created_updated_dict) for data in valid_data_list]
        with app.app_context():
            for valid in valid_list:
                db.session.add(valid)
                db.session.commit()


def set_up_scope(app: flask.app.Flask, timestamp: datetime.datetime) -> None:
    with mock_datetime_now(timestamp, datetime):
        scope01_data = {'id': uuid.UUID(SCOPE01_ID), 'user_id': uuid.UUID(ACTOR0001_USER_ID),
                        'actor_id': uuid.UUID(ACTOR0001_USER_ID), 'mode': Mode.read}
        scope02_data = {'id': uuid.UUID(SCOPE02_ID), 'user_id': uuid.UUID(ACTOR0002_USER_ID),
                        'actor_id': uuid.UUID(ACTOR0002_USER_ID), 'mode': Mode.read}
        scope03_data = {'id': uuid.UUID(SCOPE03_ID), 'user_id': uuid.UUID(USER0001_USER_ID),
                        'actor_id': uuid.UUID(ACTOR0001_USER_ID), 'mode': Mode.write}
        scope04_data = {'id': uuid.UUID(SCOPE04_ID), 'user_id': uuid.UUID(USER0002_USER_ID),
                        'actor_id': uuid.UUID(ACTOR0002_USER_ID), 'mode': Mode.write}
        scope05_data = {'id': uuid.UUID(SCOPE05_ID), 'user_id': uuid.UUID(USER0003_USER_ID),
                        'actor_id': uuid.UUID(ACTOR0001_USER_ID), 'mode': Mode.write}
        scope06_data = {'id': uuid.UUID(SCOPE06_ID), 'user_id': uuid.UUID(USER0003_USER_ID),
                        'actor_id': uuid.UUID(ACTOR0002_USER_ID), 'mode': Mode.write}

        created_updated_dict = {'created_at': datetime.datetime.now(), 'updated_at': datetime.datetime.now()}

        scope_data_list = [scope01_data, scope02_data, scope03_data, scope04_data, scope05_data, scope06_data]

        scope_list = [Scope(**data, **created_updated_dict) for data in scope_data_list]
        with app.app_context():
            for valid in scope_list:
                db.session.add(valid)
                db.session.commit()


def set_up_state(app: flask.app.Flask, timestamp: datetime.datetime) -> None:
    with mock_datetime_now(timestamp, datetime):
        state01_data = {'id': uuid.UUID(STATE01_ID), 'begin': TS_12_30_03, 'end': TS_12_30_10}
        state02_data = {'id': uuid.UUID(STATE02_ID), 'begin': TS_11_00_00, 'end': TS_12_29_00}

        created_updated_dict = {'created_at': datetime.datetime.now(), 'updated_at': datetime.datetime.now()}

        state_data_list = [state01_data, state02_data]

        state_list = [State(**data, **created_updated_dict) for data in state_data_list]
        with app.app_context():
            for valid in state_list:
                db.session.add(valid)
                db.session.commit()


class TestApiFunctions(TestCase):
    @classmethod
    def setUpClass(cls):
        cls.app = create_app(config_class=Config)
        with cls.app.app_context():
            db.drop_all()
            db.create_all()
            db.session.commit()
        cls.app_test = cls.app.test_client()

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

    def setUp(self):
        set_up_users(self.app, TS_11_00_00)
        set_up_valid(self.app, TS_11_00_00)
        set_up_scope(self.app, TS_11_00_00)
        set_up_state(self.app, TS_11_00_00)

    def tearDown(self):
        pass

    def test_get_state_error(self):
        self.fail()
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
