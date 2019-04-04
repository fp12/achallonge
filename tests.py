import os
import asyncio
import random
import string
import unittest
import json
from datetime import datetime, timedelta

import challonge


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
organization = 'achallonge-testing1'


def get_random_name():
    return "achallonge_" + "".join(random.choice(string.ascii_lowercase) for _ in range(0, 15))


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
        user = yield from challonge.get_user(username, api_key)
        tournaments = yield from user.get_tournaments()
        for t in tournaments[:]:
            if t.name.startswith('achallonge'):
                yield from user.destroy_tournament(t)


# @unittest.skip('')
class SystemTestCase(unittest.TestCase):
    @async_test
    def setUp(self):
        self.user = yield from challonge.get_user(username, api_key)

    # @unittest.skip('')
    @async_test
    def test_a_raise(self):
        random_name = get_random_name()
        t = yield from self.user.create_tournament(random_name, random_name)

        challonge.USE_EXCEPTIONS = True

        with self.assertRaises(NameError):
            yield from t.update(fake_argument=0)

        challonge.USE_EXCEPTIONS = False

        with self.assertLogs('challonge', level='WARN'):
            yield from t.update(fake_argument=0)

        challonge.USE_EXCEPTIONS = True

        yield from self.user.destroy_tournament(t)


# @unittest.skip('')
class AAUserTestCase(unittest.TestCase):
    # @unittest.skip('')
    @async_test
    def test_a_init(self):
        new_user = challonge.User(username, api_key)
        self.assertNotEqual(new_user, None)
        yield from new_user.validate()  # can raise

    # @unittest.skip('')
    @async_test
    def test_b_get_tournaments(self):
        new_user = yield from challonge.get_user(username, api_key)
        ts = yield from new_user.get_tournaments()
        self.assertIsInstance(ts, list)

        ts = yield from new_user.get_tournaments(subdomain=organization)
        self.assertIsInstance(ts, list)

        random_name = get_random_name()
        t1 = yield from new_user.create_tournament(random_name, random_name)

        t1_by_id = yield from new_user.get_tournament(t1.id)
        self.assertEqual(t1, t1_by_id)

        t1_by_url = yield from new_user.get_tournament(url=t1.url)
        self.assertEqual(t1, t1_by_url)

        t1_forced = yield from new_user.get_tournament(t1.id, force_update=True)
        self.assertEqual(t1, t1_forced)

        random_name = get_random_name()
        t2 = yield from new_user.create_tournament(random_name, random_name, subdomain=organization)
        self.assertEqual(t2.subdomain, organization)

        t2_by_url = yield from new_user.get_tournament(url=t2.url, subdomain=organization)
        self.assertEqual(t2, t2_by_url)

        with self.assertRaises(challonge.APIException):
            yield from new_user.get_tournament(-1)

        yield from new_user.destroy_tournament(t1)
        yield from new_user.destroy_tournament(t2)


# @unittest.skip('')
class ATournamentsTestCase(unittest.TestCase):
    @async_test
    def setUp(self):
        self.user = yield from challonge.get_user(username, api_key)

    # @unittest.skip('')
    @async_test
    def test_a_create_destroy(self):
        random_name = get_random_name()
        t1 = yield from self.user.create_tournament(random_name, random_name)
        self.assertEqual(t1.name, random_name)

        t_count = len(self.user.tournaments)
        yield from self.user.destroy_tournament(t1)
        self.assertEqual(len(self.user.tournaments), t_count-1)

    # @unittest.skip('')
    @async_test
    def test_aa_basic_options(self):
        random_name = get_random_name()
        t = yield from self.user.create_tournament(random_name, random_name)

        random_name = get_random_name()
        yield from t.update_name(random_name)
        self.assertEqual(t.name, random_name)

        random_url = get_random_name()
        yield from t.update_url(random_url)
        self.assertEqual(t.url, random_url)

        random_desc = get_random_name()
        yield from t.update_description(random_desc)
        self.assertEqual(t.description, random_desc)

        yield from self.user.destroy_tournament(t)

    # @unittest.skip('')
    @async_test
    def test_ab_options(self):
        random_name = get_random_name()
        t = yield from self.user.create_tournament(random_name, random_name)

        yield from t.update_website_options(hide_forum=True, show_rounds=False, open_signup=True)
        self.assertTrue(t.hide_forum)
        self.assertFalse(t.show_rounds)
        self.assertTrue(t.open_signup)

        yield from t.set_private()
        self.assertTrue(t.private)

        yield from t.set_private(False)
        self.assertFalse(t.private)

        yield from t.update_notifications(on_match_open=True, on_tournament_end=True)
        self.assertTrue(t.notify_users_when_matches_open)
        self.assertTrue(t.notify_users_when_the_tournament_ends)

        yield from t.set_max_participants(25)
        self.assertEqual(t.signup_cap, 25)

        yield from t.update_pairing_method(challonge.Pairing.sequential)
        self.assertTrue(t.sequential_pairings)

        yield from self.user.destroy_tournament(t)

    # @unittest.skip('')
    @async_test
    def test_b_add_participants(self):
        random_name = get_random_name()
        t = yield from self.user.create_tournament(random_name, random_name)

        p1 = yield from t.add_participant('p1')
        self.assertEqual(p1.name, 'p1')
        self.assertEqual(len(t.participants), 1)

        p2 = yield from t.add_participant('p2')
        self.assertNotEqual(p1.id, p2.id)
        self.assertEqual(len(t.participants), 2)

        p1_1 = yield from t.get_participant(p1.id, force_update=True)
        self.assertEqual(p1.id, p1_1.id)
        self.assertEqual(len(t.participants), 2)

        p1_2 = yield from t.get_participant(0)
        self.assertEqual(p1_2, None)

        ps = yield from t.get_participants(force_update=True)
        self.assertEqual(len(t.participants), 2)

        yield from t.remove_participant(p2)
        self.assertEqual(len(t.participants), 1)

        for p in ps:
            if p.id == p1.id:
                break
        else:
            self.fail('participant not present')

        yield from t.add_participants('p3', 'p4')
        self.assertEqual(len(t.participants), 3)

        p3 = yield from t.add_participant(display_name='fake', email='fakeemail@prov.com', seed=1, misc='some info')
        self.assertEqual(p3.misc, 'some info')
        self.assertEqual(p3.seed, 1)

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

        new_name = 'player 1'
        yield from p.change_display_name(new_name)
        self.assertEqual(p.name, new_name)

        email = 'fake@fake.com'
        yield from p.change_email(email)
        self.assertNotEqual(p.email_hash, None)

        yield from p.change_username(username)
        self.assertEqual(p.username, username)

        self.assertEqual(p.misc, None)
        new_misc = 'some interesting text'
        yield from p.change_misc(new_misc)
        self.assertEqual(new_misc, p.misc)

        yield from self.user.destroy_tournament(t)

    # @unittest.skip('')
    @async_test
    def test_e_bulk(self):
        random_name = get_random_name()
        t = yield from self.user.create_tournament(random_name, random_name)
        yield from t.add_participants('p1', 'p2', 'p3', 'p4')
        self.assertEqual(len(t.participants), 4)
        yield from self.user.destroy_tournament(t)

    @unittest.expectedFailure
    @async_test
    def test_f_checkin(self):
        challonge.USE_EXCEPTIONS = False

        random_name = get_random_name()
        t = yield from self.user.create_tournament(random_name, random_name)
        p = yield from t.add_participant(username)
        yield from t.add_participant('p1')

        max_time = 10.0

        new_start_date = datetime.now() + timedelta(minutes=5)
        total_time = 0.0
        while t.start_at is None and total_time <= max_time:
            try:
                yield from t.set_start_date(new_start_date.strftime('%Y/%m/%d'),
                                            new_start_date.strftime('%H:%M'),
                                            10)
                self.assertNotEqual(t.start_at, None, 'failed at t.set_start_date')
                self.assertNotEqual(t.check_in_duration, None, 'failed at t.set_start_date')
            except challonge.APIException:
                yield from asyncio.sleep(2.0)
                total_time += 2.0

        if total_time >= max_time:
            'failed at t.set_start_date'

        total_time = 0.0
        while p.checked_in_at is None and total_time <= max_time:
            try:
                yield from p.check_in()
                self.assertNotEqual(p.checked_in_at, None, 'failed at p.check_in()')
            except challonge.APIException:
                yield from asyncio.sleep(2.0)
                total_time += 2.0

        if total_time >= max_time:
            'failed at p.check_in()'

        try:
            yield from p.undo_check_in()
            self.assertEqual(p.checked_in_at, None)
        except challonge.APIException:
            pass

        self.assertNotEqual(t.state, 'checked_in')
        total_time = 0.0
        while t.state != 'checked_in' and total_time <= max_time:
            try:
                yield from t.process_check_ins()
                self.assertEqual(t.state, 'checked_in')
            except challonge.APIException:
                yield from asyncio.sleep(2.0)
                total_time += 2.0

        if total_time >= max_time:
            'failed at t.process_check_ins()'

        yield from t.abort_check_in()
        self.assertEqual(t.state, 'pending')

        yield from self.user.destroy_tournament(t)

        challonge.USE_EXCEPTIONS = True

        self.fail('expected failure that sometimes work')

    # @unittest.skip('')
    @async_test
    def test_g_multi_tournaments(self):
        random_name1 = get_random_name()
        t1 = yield from self.user.create_tournament(random_name1, random_name1)
        random_name2 = get_random_name()
        t2 = yield from self.user.create_tournament(random_name2, random_name2)

        t1_ref = yield from self.user.get_tournament(t1.id)
        self.assertEqual(t1, t1_ref)
        self.assertIs(t1, t1_ref)
        self.assertNotEqual(t1, t2)

        yield from self.user.destroy_tournament(t1)
        yield from self.user.destroy_tournament(t2)

    # @unittest.skip('')
    @async_test
    def test_h_participants_consistency(self):
        random_name = get_random_name()
        t = yield from self.user.create_tournament(random_name, random_name)
        p1 = yield from t.add_participant('p1')
        yield from t.add_participants('p2', 'p3', 'p4')
        yield from t.start()  # should order a refresh of participants

        self.assertTrue(p1 in t.participants)

        yield from self.user.destroy_tournament(t)

    # @unittest.skip('')
    @async_test
    def test_i_swiss(self):
        random_name = get_random_name()
        t = yield from self.user.create_tournament(random_name, random_name, challonge.TournamentType.swiss)
        self.assertEqual(t.tournament_type, challonge.TournamentType.swiss.value)

        yield from t.update_tournament_type(challonge.TournamentType.round_robin)
        self.assertNotEqual(t.tournament_type, challonge.TournamentType.swiss.value)

        yield from t.update_tournament_type(challonge.TournamentType.swiss)
        self.assertEqual(t.tournament_type, challonge.TournamentType.swiss.value)

        self.assertEqual(float(t.pts_for_match_win), 1.0)
        self.assertEqual(float(t.pts_for_match_tie), 0.5)
        self.assertEqual(float(t.pts_for_game_win), 0.0)
        self.assertEqual(float(t.pts_for_game_tie), 0.0)
        self.assertEqual(float(t.pts_for_bye), 1.0)
        yield from t.setup_swiss_points(2.0, .7, .3, .1, .5)
        self.assertEqual(float(t.pts_for_match_win), 2.0)
        self.assertEqual(float(t.pts_for_match_tie), 0.7)
        self.assertEqual(float(t.pts_for_game_win), 0.3)
        self.assertEqual(float(t.pts_for_game_tie), 0.1)
        self.assertEqual(float(t.pts_for_bye), 0.5)

        rounds = 4
        yield from t.add_participants(*[str(i) for i in range(9)])
        yield from t.setup_swiss_rounds(rounds)
        self.assertEqual(t.swiss_rounds, rounds)

        yield from t.start()
        yield from t.matches[0].report_tie('1-1')

        yield from self.user.destroy_tournament(t)

    # @unittest.skip('')
    @async_test
    def test_j_round_robin(self):
        random_name = get_random_name()
        t = yield from self.user.create_tournament(random_name, random_name, challonge.TournamentType.round_robin)
        self.assertEqual(t.tournament_type, challonge.TournamentType.round_robin.value)

        yield from t.update_tournament_type(challonge.TournamentType.swiss)
        self.assertNotEqual(t.tournament_type, challonge.TournamentType.round_robin.value)

        yield from t.update_tournament_type(challonge.TournamentType.round_robin)
        self.assertEqual(t.tournament_type, challonge.TournamentType.round_robin.value)

        self.assertEqual(float(t.rr_pts_for_match_win), 1.0)
        self.assertEqual(float(t.rr_pts_for_match_tie), 0.5)
        self.assertEqual(float(t.rr_pts_for_game_win), 0.0)
        self.assertEqual(float(t.rr_pts_for_game_tie), 0.0)
        yield from t.setup_round_robin_points(2.0, .7, .3, .1)
        self.assertEqual(float(t.rr_pts_for_match_win), 2.0)
        self.assertEqual(float(t.rr_pts_for_match_tie), 0.7)
        self.assertEqual(float(t.rr_pts_for_game_win), 0.3)
        self.assertEqual(float(t.rr_pts_for_game_tie), 0.1)

        yield from t.update_ranking_order(challonge.RankingOrder.points_scored)
        self.assertEqual(t.ranked_by, challonge.RankingOrder.points_scored.value)

        yield from self.user.destroy_tournament(t)

    # @unittest.skip('')
    @async_test
    def test_k_single_elim(self):
        random_name = get_random_name()
        t = yield from self.user.create_tournament(random_name, random_name)
        self.assertEqual(t.tournament_type, challonge.TournamentType.single_elimination.value)

        yield from t.update_tournament_type(challonge.TournamentType.swiss)
        self.assertNotEqual(t.tournament_type, challonge.TournamentType.single_elimination.value)

        yield from t.update_tournament_type(challonge.TournamentType.single_elimination)
        self.assertEqual(t.tournament_type, challonge.TournamentType.single_elimination.value)

        yield from t.set_single_elim_third_place_match(True)
        self.assertTrue(t.hold_third_place_match)

        yield from t.add_participants('p1', 'p2')
        yield from t.start()
        yield from t.matches[0].report_winner(t.participants[0], '1-0')
        yield from t.finalize()

        yield from self.user.destroy_tournament(t)

    # @unittest.skip('')
    @async_test
    def test_l_double_elim(self):
        random_name = get_random_name()
        t = yield from self.user.create_tournament(random_name, random_name, challonge.TournamentType.double_elimination)
        self.assertEqual(t.tournament_type, challonge.TournamentType.double_elimination.value)

        yield from t.update_tournament_type(challonge.TournamentType.swiss)
        self.assertNotEqual(t.tournament_type, challonge.TournamentType.double_elimination.value)

        yield from t.update_tournament_type(challonge.TournamentType.double_elimination)
        self.assertEqual(t.tournament_type, challonge.TournamentType.double_elimination.value)

        yield from t.update_double_elim_ending(challonge.DoubleEliminationEnding.no_grand_finals)

        yield from self.user.destroy_tournament(t)

    # @unittest.skip('')
    @async_test
    def test_m_get_ranking(self):
        random_name = get_random_name()
        t = yield from self.user.create_tournament(random_name, random_name)
        rankings = yield from t.get_final_ranking()
        self.assertIsNone(rankings)

        p1 = yield from t.add_participant('p1')
        p2 = yield from t.add_participant('p2')
        yield from t.start()
        yield from t.matches[0].report_winner(p1, '1-0')
        yield from t.finalize()

        rankings = yield from t.get_final_ranking()
        self.assertIn(p1, rankings[1])
        self.assertIn(p2, rankings[2])

        yield from self.user.destroy_tournament(t)

    # @unittest.skip('')
    @async_test
    def test_n_multi_rounds(self):
        random_name = get_random_name()
        t = yield from self.user.create_tournament(random_name, random_name)

        yield from t.add_participants(*('p{}'.format(i) for i in range(20)))
        yield from t.start()

        matches = yield from t.get_matches()
        for m in matches:
            if m.player1_id:
                p1 = yield from t.get_participant(m.player1_id)
                self.assertIsNotNone(p1)
                self.assertIn(p1, t.participants)
            if m.player2_id:
                p2 = yield from t.get_participant(m.player2_id)
                self.assertIsNotNone(p2)
                self.assertIn(p1, t.participants)

        yield from self.user.destroy_tournament(t)

    # @unittest.skip('')
    @async_test
    def test_o_shuffle(self):
        participants_count = 20
        random_name = get_random_name()

        t = yield from self.user.create_tournament(random_name, random_name)
        yield from t.add_participants(*['p' + str(i) for i in range(participants_count)])

        # we'll compare the seeds, and if more than half have changed, then we're good
        initial_participants_seeds = [(p.name, p.seed) for p in t.participants]
        yield from t.shuffle_participants()
        mod_count = 0
        for name, seed in initial_participants_seeds:
            p = yield from t.search_participant(name)
            self.assertIsNotNone(p, 'Could not find participant named \'{}\''.format(name))
            if p.seed != seed:
                mod_count += 1
        self.assertGreaterEqual(mod_count, participants_count // 2)


# @unittest.skip('')
class MatchesTestCase(unittest.TestCase):
    @async_test
    def setUp(self):
        self.user = yield from challonge.get_user(username, api_key)

    # @unittest.skip('')
    @async_test
    def test_a_report_live_scores(self):
        random_name = get_random_name()
        t = yield from self.user.create_tournament(random_name, random_name)
        yield from t.add_participants('p1', 'p2', 'p3', 'p4')
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
        yield from t.add_participants('p1', 'p2', 'p3', 'p4')

        p1 = yield from t.search_participant('p1')
        self.assertEqual(p1.name, 'p1')

        p_fake = yield from t.search_participant('fake', force_update=True)
        self.assertEqual(p_fake, None)

        yield from t.start()
        m = yield from t.get_matches()
        yield from m[0].report_winner(p1, '1-0')
        self.assertEqual(m[0].winner_id, p1.id)
        yield from self.user.destroy_tournament(t)

    # @unittest.skip('')
    @async_test
    def test_c_votes(self):
        random_name = get_random_name()
        t = yield from self.user.create_tournament(random_name, random_name)
        yield from t.add_participants('p1', 'p2', 'p3', 'p4')
        yield from t.start()
        m = yield from t.get_matches()
        yield from m[0].change_votes(player1_votes=3)
        self.assertEqual(m[0].player1_votes, 3)
        yield from m[0].change_votes(player1_votes=1, player2_votes=5, add=True)
        self.assertEqual(m[0].player1_votes, 4)
        self.assertEqual(m[0].player2_votes, 5)
        yield from self.user.destroy_tournament(t)

    # @unittest.skip('')
    @async_test
    def test_d_next_match_and_opponent(self):
        random_name = get_random_name()
        t = yield from self.user.create_tournament(random_name, random_name)
        p1 = yield from t.add_participant('p1')
        p2 = yield from t.add_participant('p2')
        yield from t.add_participant('p3')
        p4 = yield from t.add_participant('p4')
        yield from t.start()

        m1 = yield from p1.get_next_match()
        self.assertIsNotNone(m1)

        p4_ref = yield from p1.get_next_opponent()
        self.assertIs(p4, p4_ref)

        yield from m1.report_winner(p1, '1-0')

        m2 = yield from p1.get_next_match()
        self.assertIsNotNone(m2)
        self.assertEqual(m2.state, 'pending')
        self.assertIsNone(m2.player2_id)

        m3 = yield from p2.get_next_match()
        yield from m3.report_winner(p2, '1-0')

        self.assertEqual(m2.player2_id, p2.id)
        yield from m2.report_winner(p1, '1-0')

        m0 = yield from p1.get_next_match()
        self.assertIsNone(m0)

        p0_ref = yield from p1.get_next_opponent()
        self.assertIsNone(p0_ref)

        yield from self.user.destroy_tournament(t)

    # @unittest.skip('')
    @async_test
    def test_e_reopen(self):
        random_name = get_random_name()
        t = yield from self.user.create_tournament(random_name, random_name)
        yield from t.add_participants('p1', 'p2', 'p3', 'p4')
        yield from t.start()

        m = yield from t.get_matches()
        p1 = yield from t.search_participant('p1')
        self.assertEqual(m[0].state, 'pending')

        yield from m[0].report_winner(p1, '1-0')
        self.assertEqual(m[0].state, 'complete')

        yield from m[0].reopen()
        self.assertEqual(m[0].state, 'open')
        yield from self.user.destroy_tournament(t)


# @unittest.skip('')
class AttachmentsTestCase(unittest.TestCase):
    @async_test
    def setUp(self):
        self.user = yield from challonge.get_user(username, api_key)

    # @unittest.skip('')
    @async_test
    def test_a_url(self):
        random_name = get_random_name()
        t = yield from self.user.create_tournament(random_name, random_name)
        yield from t.allow_attachments()
        yield from t.add_participants('p1', 'p2', 'p3', 'p4')
        yield from t.start()
        m = yield from t.get_matches()

        a1 = yield from m[0].attach_url('https://github.com/fp12/achallonge')
        self.assertEqual(a1.url, 'https://github.com/fp12/achallonge')
        self.assertEqual(len(m[0].attachments), 1)

        a2 = yield from m[0].attach_url('https://github.com/fp12', description='main page')
        self.assertEqual(a2.description, 'main page')
        self.assertEqual(len(m[0].attachments), 2)

        yield from a2.change_url('https://github.com/fp12', description='GitHub portal')
        self.assertEqual(a2.description, 'GitHub portal')

        yield from m[0].destroy_attachment(a2)
        self.assertEqual(len(m[0].attachments), 1)

        m0 = yield from t.get_match(m[0].id, force_update=True)
        self.assertEqual(m[0], m0)
        self.assertEqual(len(m0.attachments), 1)

        yield from self.user.destroy_tournament(t)

    # @unittest.skip('')
    @async_test
    def test_b_text(self):
        random_name = get_random_name()
        t = yield from self.user.create_tournament(random_name, random_name)
        yield from t.allow_attachments()
        yield from t.add_participants('p1', 'p2', 'p3', 'p4')
        yield from t.start()
        m = yield from t.get_matches()

        random_text = get_random_name()
        a = yield from m[0].attach_text(random_text)
        self.assertEqual(a.description, random_text)

        random_text = get_random_name()
        yield from a.change_text(random_text)
        self.assertEqual(a.description, random_text)

        m = yield from t.get_matches(force_update=True)
        self.assertEqual(len(m[0].attachments), 1)

        yield from m[0].destroy_attachment(a)
        self.assertEqual(len(m[0].attachments), 0)

        yield from self.user.destroy_tournament(t)

    @unittest.expectedFailure
    @async_test
    def test_c_file(self):
        challonge.USE_EXCEPTIONS = False

        random_name = get_random_name()
        t = yield from self.user.create_tournament(random_name, random_name)
        yield from t.allow_attachments()
        yield from t.add_participants('p1', 'p2', 'p3', 'p4')
        yield from t.start()
        m = yield from t.get_matches()

        try:
            a = yield from m[0].attach_file('examples/listing.py', 'Simple example')
            self.assertNotEqual(a.asset_url, None)
        except challonge.APIException:
            pass

        random_text = get_random_name()
        a = yield from m[0].attach_text(random_text)

        random_text = get_random_name()
        yield from a.change_description(random_text)
        self.assertEqual(a.description, random_text)

        yield from a.change_file('examples/create.py')
        self.assertNotEqual(a.asset_url, None)

        yield from self.user.destroy_tournament(t)

        challonge.USE_EXCEPTIONS = True

        self.fail('expected failure that sometimes work')

    @unittest.expectedFailure
    @async_test
    def test_d_file(self):
        challonge.USE_EXCEPTIONS = False

        random_name = get_random_name()
        t = yield from self.user.create_tournament(random_name, random_name)
        yield from t.allow_attachments()
        yield from t.add_participants('p1', 'p2', 'p3', 'p4')
        yield from t.start()
        m = yield from t.get_matches()

        random_text = get_random_name()
        a = yield from m[0].attach_text(random_text)

        yield from a.change_file('examples/create.py')
        self.assertNotEqual(a.asset_url, None)

        yield from self.user.destroy_tournament(t)

        challonge.USE_EXCEPTIONS = True

        self.fail('expected failure that sometimes work')


if __name__ == "__main__":
    unittest.main()
