import os
import asyncio
import random
import string
import unittest
import json

from challonge import User, get_user


def get_credentials():
    username = None
    api_key = None

    secrets_file = '.secrets'
    if os.path.isfile(secrets_file):
        with open(secrets_file) as file:
            local_secrets = json.load(file)
            username = local_secrets['username']
            api_key = local_secrets['api_key']

    username = os.environ.get('CHALLONGE_USER') if username is None else username
    api_key = os.environ.get('CHALLONGE_KEY') if api_key is None else api_key
    if not username or not api_key:
        raise RuntimeError('You must add CHALLONGE_USER and CHALLONGE_KEY to your environment variables to run the test suite')

    return username, api_key


username, api_key = get_credentials()


def get_random_name():
    return "pychallonge_" + "".join(random.choice(string.ascii_lowercase) for _ in range(0, 15))


def async_test(f):
    def wrapper(*args, **kwargs):
        coro = asyncio.coroutine(f)
        future = coro(*args, **kwargs)
        loop = asyncio.get_event_loop()
        loop.run_until_complete(future)
    return wrapper


class AAACleanup(unittest.TestCase):
    """ Cleans up previously created tournaments via these tests
    if they were interrupted
    """
    @async_test
    def test_cleanup(self):
        user = yield from get_user(username, api_key)
        tournaments = yield from user.get_tournaments()
        for t in tournaments[:]:
            if t.name.startswith('pychallonge'):
                yield from user.destroy_tournament(t)


# @unittest.skip('')
class UserTestCase(unittest.TestCase):
    # @unittest.skip('')
    @async_test
    def test_a_init(self):
        new_user = User(username, api_key)
        self.assertNotEqual(new_user, None)
        yield from new_user.validate()  # can raise

    # @unittest.skip('')
    @async_test
    def test_b_get_tournaments(self):
        new_user = yield from get_user(username, api_key)
        t = yield from new_user.get_tournaments()
        self.assertIsInstance(t, list)


# @unittest.skip('')
class TournamentsTestCase(unittest.TestCase):
    @async_test
    def setUp(self):
        self.user = yield from get_user(username, api_key)

    # @unittest.skip('')
    @async_test
    def test_a_create_destroy(self):
        random_name = get_random_name()
        t = yield from self.user.create_tournament(random_name, random_name)
        self.assertEqual(t.name, random_name)
        t2 = yield from self.user.get_tournament(t.id)
        self.assertEqual(t.id, t2.id)
        self.assertEqual(len(self.user.tournaments), 1)
        yield from self.user.destroy_tournament(t)
        self.assertEqual(len(self.user.tournaments), 0)

    # @unittest.skip('')
    @async_test
    def test_b_add_participants(self):
        random_name = get_random_name()
        t = yield from self.user.create_tournament(random_name, random_name)
        p1 = yield from t.add_participant('p1')
        self.assertEqual(p1.name, 'p1')
        p2 = yield from t.add_participant('p2')
        self.assertNotEqual(p1.id, p2.id)
        p1_1 = yield from t.get_participant(p1.id, force_update=True)
        self.assertEqual(p1.id, p1_1.id)
        ps = yield from t.get_participants(force_update=True)
        remaining = yield from t.remove_participant(p2, get_participants=True)
        self.assertEqual(len(remaining), 1)
        for p in ps:
            if p.id == p1.id:
                break
        else:
            self.fail('participant not present')
        yield from self.user.destroy_tournament(t)

    # @unittest.skip('')
    @async_test
    def test_c_start_reset(self):
        random_name = get_random_name()
        t = yield from self.user.create_tournament(random_name, random_name)
        yield from t.add_participant('p1')
        yield from t.add_participant('p2')
        self.assertEqual(t.state, 'pending')
        yield from t.start()
        self.assertEqual(t.state, 'underway')
        yield from t.reset()
        self.assertEqual(t.state, 'pending')
        yield from self.user.destroy_tournament(t)

    # @unittest.skip('')
    @async_test
    def test_d_update_participants(self):
        random_name = get_random_name()
        t = yield from self.user.create_tournament(random_name, random_name)
        p = yield from t.add_participant('p1')
        yield from t.add_participant('p2')
        yield from t.add_participant('p3')
        yield from t.add_participant('p4')
        self.assertEqual(p.seed, 1)
        yield from p.change_seed(2)
        self.assertEqual(p.seed, 2)
        yield from self.user.destroy_tournament(t)

    # @unittest.skip('')
    @async_test
    def test_e_bulk(self):
        random_name = get_random_name()
        t = yield from self.user.create_tournament(random_name, random_name)
        yield from t.add_participants(['p1', 'p2', 'p3', 'p4'])
        self.assertEqual(len(t.participants), 4)
        yield from self.user.destroy_tournament(t)


# @unittest.skip('')
class MatchesTestCase(unittest.TestCase):
    @async_test
    def setUp(self):
        self.user = yield from get_user(username, api_key)

    # @unittest.skip('')
    @async_test
    def test_a_report_live_scores(self):
        random_name = get_random_name()
        t = yield from self.user.create_tournament(random_name, random_name)
        yield from t.add_participants(['p1', 'p2', 'p3', 'p4'])
        yield from t.start()
        self.assertEqual(t.state, 'underway', random_name)
        m = yield from t.get_matches()
        self.assertGreater(len(m), 0, random_name)
        yield from m[0].report_live_scores('1-0')
        self.assertEqual(m[0].scores_csv, '1-0', random_name)
        yield from m[0].report_live_scores('0-1')
        self.assertEqual(m[0].scores_csv, '0-1', random_name)
        yield from m[0].report_live_scores('1-0,0-1')
        self.assertEqual(m[0].scores_csv, '1-0,0-1', random_name)
        yield from self.user.destroy_tournament(t)

    # @unittest.skip('')
    @async_test
    def test_b_report_winner(self):
        random_name = get_random_name()
        t = yield from self.user.create_tournament(random_name, random_name)
        yield from t.add_participants(['p1', 'p2', 'p3', 'p4'])
        p1 = yield from t.search_participant('p1')
        self.assertEqual(p1.name, 'p1')
        yield from t.start()
        m = yield from t.get_matches()
        yield from m[0].report_winner(p1, '1-0')
        self.assertEqual(m[0].winner_id, p1.id)
        yield from self.user.destroy_tournament(t)


# @unittest.skip('')
class AttachmentsTestCase(unittest.TestCase):
    @async_test
    def setUp(self):
        self.user = yield from get_user(username, api_key)

    # @unittest.skip('')
    @async_test
    def test_a_url(self):
        random_name = get_random_name()
        t = yield from self.user.create_tournament(random_name, random_name)
        yield from t.allow_attachments()
        yield from t.add_participants(['p1', 'p2', 'p3', 'p4'])
        yield from t.start()
        m = yield from t.get_matches()
        a = yield from m[0].attach_url('https://github.com/fp12/achallonge')
        self.assertEqual(a.url, 'https://github.com/fp12/achallonge')
        a = yield from m[0].attach_url('https://github.com/fp12', description='main page')
        self.assertEqual(a.description, 'main page')
        yield from self.user.destroy_tournament(t)

    # @unittest.skip('')
    @async_test
    def test_b_text(self):
        random_name = get_random_name()
        t = yield from self.user.create_tournament(random_name, random_name)
        yield from t.allow_attachments()
        yield from t.add_participants(['p1', 'p2', 'p3', 'p4'])
        yield from t.start()
        m = yield from t.get_matches()
        random_text = get_random_name()
        a = yield from m[0].attach_text(random_text)
        self.assertEqual(a.description, random_text)
        yield from self.user.destroy_tournament(t)


if __name__ == "__main__":
    unittest.main()
