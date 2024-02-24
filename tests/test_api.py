import datetime
import time
from unittest import TestCase
from app.app import user_db, keys_db, actor_db, state_db, KeyType, get_state, set_state

d = keys_db()

from unittest.mock import Mock


class ApiTest(TestCase):
    def setUp(self):
        keys_db().clear()
        user_db().clear()
        actor_db().clear()
        state_db().clear()

        keys_db()['052b3945b6913a005c74c52d0a2c48cfc7c10207db775d51950a21bc12dcc472'] = {
            'type': KeyType.USER, 'ref_id': '0001'}
        keys_db()['781bd77d28bf4c53e13719136180dcef2d54c75b37b8a3553339859255731d9d'] = {
            'type': KeyType.USER, 'ref_id': '0002'}
        keys_db()['8c267d03891a23661ec3e89dbed546297cb86bae05d4767ff01cc0b1616d3499'] = {
            'type': KeyType.USER, 'ref_id': '0003'}
        keys_db()['9a9893b036fd1708c518467a203de7405184feff1c2eb315ee8099cd8fedab58'] = {
            'type': KeyType.ACTOR, 'ref_id': 'abcd'}
        keys_db()['f160e336939ee5b8ed3206962c488fc5be3f6e35a3ca92fc170e80657958bda3'] = {
            'type': KeyType.ACTOR, 'ref_id': 'efgh'}

        user_db()['0001'] = {'actor_ids': ['abcd']}
        user_db()['0002'] = {'actor_ids': ['efgh']}
        user_db()['0003'] = {'actor_ids': ['abcd', 'efgh']}

        actor_db()['abcd'] = {'name': 'door street', 'timeout': 5}
        actor_db()['efgh'] = {'name': 'door flat', 'timeout': 5}

    def tearDown(self):
        pass

    def test_get_state_initial(self):
        # get initial state for actor "abcd"

        self.assertEqual((200, {'abcd': (200, False)}),
                         get_state(['abcd'], '9a9893b036fd1708c518467a203de7405184feff1c2eb315ee8099cd8fedab58'))

        # get initial state for actor f160..
        self.assertEqual((200, {'efgh': (200, False)}),
                         get_state(['efgh'], 'f160e336939ee5b8ed3206962c488fc5be3f6e35a3ca92fc170e80657958bda3'))

    def test_get_state_error(self):
        # get initial state for a wrong key
        self.assertEqual((400, {'msg': 'permission denied'}),
                         get_state(['abcd'], 'abcde336939ee5b8ed3206962c488fc5be3f6e35a3ca92fc170e80657958bda3'))

        # get initial state for a wrong actor id
        self.assertEqual((200, {'wxyz': (400, False)}),
                         get_state(['wxyz'], 'f160e336939ee5b8ed3206962c488fc5be3f6e35a3ca92fc170e80657958bda3'))

        # get initial state for an existing actor id, but with a key that is lacking permission
        self.assertEqual((200, {'efgh': (200, False)}),
                         get_state(['efgh'], '9a9893b036fd1708c518467a203de7405184feff1c2eb315ee8099cd8fedab58'))

        keys_db()['9999d77d28bf4c53e13719136180dcef2d54c75b37b8a3553339859255731d9d'] = {}
        self.assertEqual((403, {'msg': 'db error'}),
                         get_state(['efgh'], '9999d77d28bf4c53e13719136180dcef2d54c75b37b8a3553339859255731d9d'))
        keys_db()['9999d77d28bf4c53e13719136180dcef2d54c75b37b8a3553339859255731d9d'] = {'type': KeyType.USER}
        self.assertEqual((403, {'msg': 'db error'}),
                         get_state(['efgh'], '9999d77d28bf4c53e13719136180dcef2d54c75b37b8a3553339859255731d9d'))
        keys_db()['9999d77d28bf4c53e13719136180dcef2d54c75b37b8a3553339859255731d9d'] = {'ref_id': '0002'}
        self.assertEqual((403, {'msg': 'db error'}),
                         get_state(['efgh'], '9999d77d28bf4c53e13719136180dcef2d54c75b37b8a3553339859255731d9d'))

    def test_check_key01(self):
        # assert initial states are as expected
        self.test_get_state_initial()

        # enable state for actor 9a98... with user 0001
        self.assertEqual((200, {'abcd': 200}),
                         set_state(['abcd'], '052b3945b6913a005c74c52d0a2c48cfc7c10207db775d51950a21bc12dcc472'))

        # get states for actors 9a98... and f160...
        self.assertEqual((200, {'abcd': (200, True)}),
                         get_state(['abcd'], '9a9893b036fd1708c518467a203de7405184feff1c2eb315ee8099cd8fedab58'))
        self.assertEqual((200, {'efgh': (200, False)}),
                         get_state(['efgh'], 'f160e336939ee5b8ed3206962c488fc5be3f6e35a3ca92fc170e80657958bda3'))

        # ToDo: mock datetime.datetime.now() to simulate time before and after the timeout; also: sanitizing

    def test_check_key02(self):
        # assert initial states are as expected
        self.test_get_state_initial()

        # enable state for actor f160... with user 0002
        self.assertEqual((200, {'efgh': 200}),
                         set_state(['efgh'], '781bd77d28bf4c53e13719136180dcef2d54c75b37b8a3553339859255731d9d'))

        # get states for actors 9a98... and f160...
        self.assertEqual((200, {'abcd': (200, False)}),
                         get_state(['abcd'], '9a9893b036fd1708c518467a203de7405184feff1c2eb315ee8099cd8fedab58'))
        self.assertEqual((200, {'efgh': (200, True)}),
                         get_state(['efgh'], 'f160e336939ee5b8ed3206962c488fc5be3f6e35a3ca92fc170e80657958bda3'))

        # ToDo: mock datetime.datetime.now() to simulate time before and after the timeout; also: sanitizing

    def test_check_key03(self):
        # assert initial states are as expected
        self.test_get_state_initial()

        # enable state for actor 9a98... and f160... with user 0003
        self.assertEqual((200, {'abcd': 200, 'efgh': 200}),
                         set_state(['abcd', 'efgh'],
                                   '8c267d03891a23661ec3e89dbed546297cb86bae05d4767ff01cc0b1616d3499'))

        # get initial state for actor 9a98...
        self.assertEqual((200, {'abcd': (200, True)}),
                         get_state(['abcd'], '9a9893b036fd1708c518467a203de7405184feff1c2eb315ee8099cd8fedab58'))
        print('##' + str(state_db()))
        self.assertEqual((200, {'efgh': (200, True)}),
                         get_state(['efgh'], 'f160e336939ee5b8ed3206962c488fc5be3f6e35a3ca92fc170e80657958bda3'))

        # ToDo: mock datetime.datetime.now() to simulate time before and after the timeout; also: sanitizing

    def test_sanitize_state_db(self):
        # assert initial states are as expected
        self.test_get_state_initial()

        # enable state for actor 9a98... with user 0001
        self.assertEqual((200, {'abcd': 200}),
                         set_state(['abcd'], '052b3945b6913a005c74c52d0a2c48cfc7c10207db775d51950a21bc12dcc472'))

        # get initial state for actor 9a98..
        self.assertEqual((200, {'abcd': (200, True)}),
                         get_state(['abcd'], '9a9893b036fd1708c518467a203de7405184feff1c2eb315ee8099cd8fedab58'))
        # manually set last_on to a future date
        state_db()['abcd']['last_on'] = datetime.datetime.now() + datetime.timedelta(hours=1)
        # check if sanitazation works as expected (state will be set to None, thereby evaluating to false below
        # assert that second actor is still false
        self.assertEqual((200, {'efgh': (200, False)}),
                         get_state(['efgh'], 'f160e336939ee5b8ed3206962c488fc5be3f6e35a3ca92fc170e80657958bda3'))
        self.assertEqual((200, {'abcd': (200, False)}),
                         get_state(['abcd'], '9a9893b036fd1708c518467a203de7405184feff1c2eb315ee8099cd8fedab58'))
        [get_state(['abcd'], '9a9893b036fd1708c518467a203de7405184feff1c2eb315ee8099cd8fedab58') for _ in range(10)]
        self.assertEqual((200, {'abcd': (200, False)}),
                         get_state(['abcd'], '9a9893b036fd1708c518467a203de7405184feff1c2eb315ee8099cd8fedab58'))
