import random
import string
from unittest import TestCase

from app.api.func import assert_password_properties
from app.util.util import hash_salt_pw_str, check_pw_str


class TestApiFunctions(TestCase):

    def test_set_password(self):
        password_set = set()
        while len(password_set) < 11:
            new_pw = ''.join([random.choice(string.ascii_letters + string.digits + string.punctuation) for _ in range(10)])
            try:
                assert_password_properties(new_pw)
            except AssertionError:
                continue
            password_set.add(new_pw)

        prior_password = password_set.pop()

        for password in password_set:
            hashed_salted_pw = hash_salt_pw_str(password)
            self.assertTrue(check_pw_str(password, hashed_salted_pw), f'mismatch: "{password=}", "{hashed_salted_pw=}"')
            self.assertFalse(check_pw_str(password, hash_salt_pw_str(prior_password)))
            prior_password = password
