from datetime import datetime
from collections import OrderedDict

from . import AUTO_GET_PARTICIPANTS, AUTO_GET_MATCHES
from .helpers import FieldHolder, assert_or_raise
from .participant import Participant
from .match import Match
from .enums import TournamentType, TournamentState, Pairing, DoubleEliminationEnding, RankingOrder


class Tournament(metaclass=FieldHolder):
    """ Representation of a Challonge tournament """

    _fields = ['accept_attachments', 'allow_participant_match_reporting',
               'anonymous_voting', 'category', 'check_in_duration',
               'completed_at', 'created_at', 'created_by_api',
               'credit_capped', 'description', 'game_id',
               'group_stages_enabled', 'hide_forum', 'hide_seeds',
               'hold_third_place_match', 'id', 'max_predictions_per_user',
               'name', 'notify_users_when_matches_open',
               'notify_users_when_the_tournament_ends', 'open_signup',
               'participants_count', 'prediction_method',
               'predictions_opened_at', 'private', 'progress_meter',
               'pts_for_bye', 'pts_for_game_tie', 'pts_for_game_win',
               'pts_for_match_tie', 'pts_for_match_win', 'quick_advance',
               'ranked_by', 'require_score_agreement',
               'rr_pts_for_game_tie', 'rr_pts_for_game_win',
               'rr_pts_for_match_tie', 'rr_pts_for_match_win',
               'sequential_pairings', 'show_rounds', 'signup_cap',
               'start_at', 'started_at', 'started_checking_in_at',
               'state', 'swiss_rounds', 'teams', 'tie_breaks',
               'tournament_type', 'updated_at', 'url',
               'description_source', 'subdomain',
               'full_challonge_url', 'live_image_url',
               'sign_up_url', 'review_before_finalizing',
               'accepting_predictions', 'participants_locked',
               'game_name', 'participants_swappable',
               'team_convertable', 'group_stages_were_started',
               'locked_at', 'event_id', 'public_predictions_before_start_time',
               'ranked', 'grand_finals_modifier', 'predict_the_losers_bracket']

    _update_parameters = ['name', 'tournament_type', 'url', 'subdomain', 'description', 'open_signup', 'hold_third_place_match',
                          'pts_for_match_win', 'pts_for_match_tie', 'pts_for_game_win', 'pts_for_game_tie', 'pts_for_bye', 'swiss_rounds',
                          'ranked_by', 'rr_pts_for_match_win', 'rr_pts_for_match_tie', 'rr_pts_for_game_win', 'rr_pts_for_game_tie',
                          'accept_attachments', 'hide_forum', 'show_rounds', 'private', 'notify_users_when_matches_open', 'notify_users_when_the_tournament_ends',
                          'sequential_pairings', 'signup_cap', 'start_at', 'check_in_duration', 'grand_finals_modifier']

    def __init__(self, connection, json_def, **kwargs):
        self.connection = connection

        self.participants = None
        self._create_participant = lambda p: self._create_holder(Participant, p, tournament=self)

        self.matches = None
        self._create_match = lambda m: self._create_holder(Match, m, tournament=self)
        self._find_match = lambda m_id: self._find_holder(self.matches, m_id)

        self._refresh_from_json(json_def)

    def _find_participant(self, p_id):
        if self.participants is not None:
            for p in self.participants:
                if int(p_id) == p.id or int(p_id) in p.group_player_ids:
                    return p
        return None

    def _refresh_from_json(self, json_def):
        if 'tournament' in json_def:
            t_data = json_def['tournament']
            self._get_from_dict(t_data)

            if 'participants' in t_data:
                self._refresh_participants_from_json(t_data['participants'])
            if 'matches' in t_data:
                self._refresh_matches_from_json(t_data['matches'])

    def _refresh_participants_from_json(self, participants_data):
        if self.participants is None:
            self.participants = [self._create_participant(p_data) for p_data in participants_data]
        else:
            for p_data in participants_data:
                for p in self.participants:
                    if p_data['participant']['id'] == p._id:
                        p._refresh_from_json(p_data)
                        break
                else:
                    self.participants.append(self._create_participant(p_data))

    def _refresh_matches_from_json(self, matches_data):
        if self.matches is None:
            self.matches = [self._create_match(m_data) for m_data in matches_data]
        else:
            for m_data in matches_data:
                for m in self.matches:
                    if m_data['match']['id'] == m._id:
                        m._refresh_from_json(m_data)
                        break
                else:
                    self.matches.append(self._create_match(m_data))

    def _add_participant(self, p: Participant):
        if p is not None:
            if self.participants is None:
                self.participants = [p]
            else:
                self.participants.append(p)

    async def start(self):
        """ start the tournament on Challonge

        |methcoro|

        Note:
            |from_api| Start a tournament, opening up first round matches for score reporting. The tournament must have at least 2 participants.

        Raises:
            APIException

        """
        params = {
                'include_participants': 1 if AUTO_GET_PARTICIPANTS else 0,
                'include_matches': 1 if AUTO_GET_MATCHES else 0
            }
        res = await self.connection('POST', 'tournaments/{}/start'.format(self._id), **params)
        self._refresh_from_json(res)

    async def reset(self):
        """ reset the tournament on Challonge

        |methcoro|

        Note:
            |from_api| Reset a tournament, clearing all of its scores and attachments. You can then add/remove/edit participants before starting the tournament again.

        Raises:
            APIException

        """
        params = {
                'include_participants': 1 if AUTO_GET_PARTICIPANTS else 0,
                'include_matches': 1 if AUTO_GET_MATCHES else 0
            }
        res = await self.connection('POST', 'tournaments/{}/reset'.format(self._id), **params)
        self._refresh_from_json(res)

    async def finalize(self):
        """ finalize the tournament on Challonge

        |methcoro|

        Note:
            |from_api| Finalize a tournament that has had all match scores submitted, rendering its results permanent.

        Raises:
            APIException

        """
        params = {
                'include_participants': 1 if AUTO_GET_PARTICIPANTS else 0,
                'include_matches': 1 if AUTO_GET_MATCHES else 0
            }
        res = await self.connection('POST', 'tournaments/{}/finalize'.format(self._id), **params)
        self._refresh_from_json(res)

    async def update(self, **params):
        """ update some parameters of the tournament

        Use this function if you want to update multiple options at once, but prefer helpers functions like :func:`allow_attachments`, :func:`set_start_date`...

        |methcoro|

        Args:
            params: one or more of: ``name`` ``tournament_type`` ``url`` ``subdomain`` ``description`` ``open_signup``
                                    ``hold_third_place_match`` ``pts_for_match_win`` ``pts_for_match_tie`` ``pts_for_game_win``
                                    ``pts_for_game_tie`` ``pts_for_bye`` ``swiss_rounds`` ``ranked_by`` ``rr_pts_for_match_win``
                                    ``rr_pts_for_match_tie`` ``rr_pts_for_game_win`` ``rr_pts_for_game_tie`` ``accept_attachments``
                                    ``hide_forum`` ``show_rounds`` ``private`` ``notify_users_when_matches_open``
                                    ``notify_users_when_the_tournament_ends`` ``sequential_pairings`` ``signup_cap``
                                    ``start_at`` ``check_in_duration`` ``grand_finals_modifier``

        Raises:
            APIException

        """
        assert_or_raise(all(k in self._update_parameters for k in params.keys()),
                        NameError,
                        'Wrong parameter given')

        res = await self.connection('PUT',
                                    'tournaments/{}'.format(self._id),
                                    'tournament',
                                    **params)
        self._refresh_from_json(res)

    async def update_tournament_type(self, tournament_type: TournamentType):
        """

        |methcoro|

        Args:
            tournament_type: choose between TournamentType.single_elimination, TournamentType.double_elimination, TournamentType.round_robin, TournamentType.swiss

        Raises:
            APIException

        """
        await self.update(tournament_type=tournament_type.value)

    async def update_name(self, new_name: str):
        """

        |methcoro|

        Args:
            new_name: the name to be changed to (Max: 60 characters)

        Raises:
            APIException

        """
        # TODO: check str 60 chars
        await self.update(name=new_name)

    async def update_url(self, new_url: str):
        """

        |methcoro|

        Args:
            new_url: the url to be changed to (challonge.com/url - letters, numbers, and underscores only)

        Raises:
            APIException

        """
        # TODO: check format
        await self.update(url=new_url)

    async def update_subdomain(self, new_subdomain: str):
        """

        |methcoro|

        Args:
            new_subdomain: the subdomain to be changed to (subdomain.challonge.com/url - letters, numbers, and underscores only)

        Raises:
            APIException: if you don't have write access to this subdomain

        """
        # TODO: check format
        await self.update(subdomain=new_subdomain)

    async def update_description(self, new_description: str):
        """

        |methcoro|

        Args:
            new_description: the description to be changed to

        Raises:
            APIException

        """
        await self.update(description=new_description)

    async def allow_attachments(self, allow: bool = True):
        """ allow this tournament to accept attachments or not

        |methcoro|

        Args:
            allow (default=True): False to disallow

        Raises:
            APIException

        """
        await self.update(accept_attachments=allow)

    async def set_start_date(self, date: str, time: str, check_in_duration: int = None):
        """ set the tournament start date (and check in duration)

        |methcoro|

        Args:
            date: fomatted date as YYYY/MM/DD (2017/02/14)
            time: fromatted time as HH:MM (20:15)
            check_in_duration (optional): duration in minutes

        Raises:
            APIException

        """
        date_time = datetime.strptime(date + ' ' + time, '%Y/%m/%d %H:%M')
        res = await self.connection('PUT',
                                    'tournaments/{}'.format(self._id),
                                    'tournament',
                                    start_at=date_time,
                                    check_in_duration=check_in_duration or 0)
        self._refresh_from_json(res)

    async def update_double_elim_ending(self, ending: DoubleEliminationEnding):
        """ update the ending format for your Double Elimination tournament

        |methcoro|

        Args:
            ending: choose between:\
            * DoubleEliminationEnding.default:  give the winners bracket finalist two chances to beat the losers bracket finalist
            * DoubleEliminationEnding.single_match: create only one grand finals match
            * DoubleEliminationEnding.no_grand_finals: don't create a finals match between winners and losers bracket finalists

        Raises:
            APIException

        """
        await self.update(grand_finals_modifier=ending.value)

    async def set_single_elim_third_place_match(self, play_third_place_match: bool):
        """

        |methcoro|

        Args:
            play_third_place_match: Include a match between semifinal losers if True

        Raises:
            APIException

        """
        await self.update(hold_third_place_match=play_third_place_match)

    async def setup_swiss_points(self, match_win: float = None, match_tie: float = None, game_win: float = None, game_tie: float = None, bye: float = None):
        """

        |methcoro|

        Args:
            match_win
            match_tie
            game_win
            game_tie
            bye

        Raises:
            APIException

        """
        params = {}
        if match_win is not None:
            params['pts_for_match_win'] = match_win
        if match_win is not None:
            params['pts_for_match_tie'] = match_tie
        if match_win is not None:
            params['pts_for_game_win'] = game_win
        if match_win is not None:
            params['pts_for_game_tie'] = game_tie
        if match_win is not None:
            params['pts_for_bye'] = bye
        assert_or_raise(len(params) > 0, ValueError, 'At least one of the points must be given')
        await self.update(**params)

    async def setup_swiss_rounds(self, rounds_count: int):
        """

        |methcoro|

        Note:
            |from_api| We recommend limiting the number of rounds to less than two-thirds the number of players. Otherwise, an impossible pairing situation can be reached and your tournament may end before the desired number of rounds are played.

        Args:
            rounds_count:

        Raises:
            APIException

        """
        await self.update(swiss_rounds=rounds_count)

    async def setup_round_robin_points(self, match_win: float = None, match_tie: float = None, game_win: float = None, game_tie: float = None):
        """

        |methcoro|

        Args:
            match_win
            match_tie
            game_win
            game_tie

        Raises:
            APIException

        """
        params = {}
        if match_win is not None:
            params['rr_pts_for_match_win'] = match_win
        if match_win is not None:
            params['rr_pts_for_match_tie'] = match_tie
        if match_win is not None:
            params['rr_pts_for_game_win'] = game_win
        if match_win is not None:
            params['rr_pts_for_game_tie'] = game_tie
        assert_or_raise(len(params) > 0, ValueError, 'At least one of the points must be given')
        await self.update(**params)

    async def update_notifications(self, on_match_open: bool = None, on_tournament_end: bool = None):
        """ update participants notifications for this tournament

        |methcoro|

        Args:
            on_match_open: Email registered Challonge participants when matches open up for them
            on_tournament_end: Email registered Challonge participants the results when this tournament ends

        Raises:
            APIException

        """
        params = {}
        if on_match_open is not None:
            params['notify_users_when_matches_open'] = on_match_open
        if on_tournament_end is not None:
            params['notify_users_when_the_tournament_ends'] = on_tournament_end
        assert_or_raise(len(params) > 0, ValueError, 'At least one of the notifications must be given')
        await self.update(**params)

    async def set_max_participants(self, max_participants: int):
        """

        |methcoro|

        Args:
            max_participants: Maximum number of participants in the bracket. A waiting list (attribute on Participant) will capture participants once the cap is reached.

        Raises:
            APIException

        """
        await self.update(signup_cap=max_participants)

    async def set_private(self, private: bool = True):
        """ Hide this tournament from the public browsable index and your profile

        |methcoro|

        Args:
            private:

        Raises:
            APIException

        """
        await self.update(private=private)

    async def update_ranking_order(self, order: RankingOrder):
        """

        |methcoro|

        Args:
            order: see :class:`RankingOrder`

        Raises:
            APIException

        """
        await self.update(ranked_by=order.value)

    async def update_website_options(self, hide_forum: bool = None, show_rounds: bool = None, open_signup: bool = None):
        """

        |methcoro|

        Args:
            hide_forum: Hide the forum tab on your Challonge page
            show_rounds: Double Elimination only - Label each round above the bracket
            open_signup: Have Challonge host a sign-up page (otherwise, you manually add all participants)

        Raises:
            APIException

        """
        params = {}
        if hide_forum is not None:
            params['hide_forum'] = hide_forum
        if show_rounds is not None:
            params['show_rounds'] = show_rounds
        if open_signup is not None:
            params['open_signup'] = open_signup
        assert_or_raise(len(params) > 0, ValueError, 'At least one of the options must be given')
        await self.update(**params)

    async def update_pairing_method(self, pairing: Pairing):
        """

        |methcoro|

        Args:
            pairing:

        Raises:
            APIException

        """
        do_sequential_pairing = pairing == Pairing.sequential
        await self.update(sequential_pairings=do_sequential_pairing)

    async def get_participant(self, p_id: int, force_update=False) -> Participant:
        """ get a participant by its id

        |methcoro|

        Args:
            p_id: participant id
            force_update (dfault=False): True to force an update to the Challonge API

        Returns:
            Participant: None if not found

        Raises:
            APIException

        """
        found_p = self._find_participant(p_id)
        if force_update or found_p is None:
            await self.get_participants()
            found_p = self._find_participant(p_id)
        return found_p

    async def get_participants(self, force_update=False) -> list:
        """ get all participants

        |methcoro|

        Args:
            force_update (default=False): True to force an update to the Challonge API

        Returns:
            list[Participant]:

        Raises:
            APIException

        """
        if force_update or self.participants is None:
            res = await self.connection('GET', 'tournaments/{}/participants'.format(self._id))
            self._refresh_participants_from_json(res)
        return self.participants or []

    async def search_participant(self, name, force_update=False):
        """ search a participant by (display) name

        |methcoro|

        Args:
            name: display name of the participant
            force_update (dfault=False): True to force an update to the Challonge API

        Returns:
            Participant: None if not found

        Raises:
            APIException

        """
        if force_update or self.participants is None:
            await self.get_participants()
        if self.participants is not None:
            for p in self.participants:
                if p.name == name:
                    return p
        return None

    async def add_participant(self, display_name: str = None, username: str = None, email: str = None, seed: int = 0, misc: str = None, **params):
        """ add a participant to the tournament

        |methcoro|

        Args:
            display_name: The name displayed in the bracket/schedule - not required if email or challonge_username is provided. Must be unique per tournament.
            username: Provide this if the participant has a Challonge account. He or she will be invited to the tournament.
            email: Providing this will first search for a matching Challonge account. If one is found, this will have the same effect as the "challonge_username" attribute. If one is not found, the "new-user-email" attribute will be set, and the user will be invited via email to create an account.
            seed: The participant's new seed. Must be between 1 and the current number of participants (including the new record). Overwriting an existing seed will automatically bump other participants as you would expect.
            misc: Max: 255 characters. Multi-purpose field that is only visible via the API and handy for site integration (e.g. key to your users table)
            params: optional params (see http://api.challonge.com/v1/documents/participants/create)

        Returns:
            Participant: newly created participant

        Raises:
            APIException

        """
        assert_or_raise((display_name is None) ^ (username is None),
                        ValueError,
                        'One of display_name or username must not be None')

        params.update({
            'name': display_name or '',
            'challonge_username': username or '',
        })
        if email is not None:
            params.update({'email': email})
        if seed != 0:
            params.update({'seed': seed})
        if misc is not None:
            params.update({'misc': misc})
        res = await self.connection('POST',
                                    'tournaments/{}/participants'.format(self._id),
                                    'participant',
                                    **params)
        new_p = self._create_participant(res)
        self._add_participant(new_p)
        return new_p

    async def add_participants(self, *names: str) -> list:
        """

        |methcoro|

        Warnings:
            |inprogress|

        Raises:
            APIException

        """
        params = {'name': list(names)}
        res = await self.connection('POST',
                                    'tournaments/{}/participants/bulk_add'.format(self._id),
                                    'participants[]',
                                    **params)
        self._refresh_participants_from_json(res)

    async def remove_participant(self, p: Participant):
        """ remove a participant from the tournament

        |methcoro|

        Args:
            p: the participant to remove

        Raises:
            APIException

        """
        await self.connection('DELETE', 'tournaments/{}/participants/{}'.format(self._id, p._id))
        if p in self.participants:
            self.participants.remove(p)

    async def get_match(self, m_id, force_update=False) -> Match:
        """ get a single match by id

        |methcoro|

        Args:
            m_id: match id
            force_update (default=False): True to force an update to the Challonge API

        Returns:
            Match

        Raises:
            APIException

        """
        found_m = self._find_match(m_id)
        if force_update or found_m is None:
            await self.get_matches()
            found_m = self._find_match(m_id)
        return found_m

    async def get_matches(self, force_update=False) -> list:
        """ get all matches (once the tournament is started)

        |methcoro|

        Args:
            force_update (default=False): True to force an update to the Challonge API

        Returns:
            list[Match]:

        Raises:
            APIException

        """
        if force_update or self.matches is None:
            res = await self.connection('GET',
                                        'tournaments/{}/matches'.format(self._id),
                                        include_attachments=1)
            self._refresh_matches_from_json(res)
        return self.matches or []

    async def shuffle_participants(self):
        """ Shuffle participants' seeds

        |methcoro|

        Note:
            |from_api| Randomize seeds among participants. Only applicable before a tournament has started.

        Raises:
            APIException

        """
        res = await self.connection('POST', 'tournaments/{}/participants/randomize'.format(self._id))
        self._refresh_participants_from_json(res)

    async def process_check_ins(self):
        """ finalize the check in phase

        |methcoro|

        Warning:
            |unstable|

        Note:
            |from_api| This should be invoked after a tournament's check-in window closes before the tournament is started.
            1. Marks participants who have not checked in as inactive.
            2. Moves inactive participants to bottom seeds (ordered by original seed).
            3. Transitions the tournament state from 'checking_in' to 'checked_in'
            NOTE: Checked in participants on the waiting list will be promoted if slots become available.

        Raises:
            APIException

        """
        params = {
                'include_participants': 1,  # forced to 1 since we need to update the Participant instances
                'include_matches': 1 if AUTO_GET_MATCHES else 0
            }
        res = await self.connection('POST', 'tournaments/{}/process_check_ins'.format(self._id), **params)
        self._refresh_from_json(res)

    async def abort_check_in(self):
        """ Abort the check in process

        |methcoro|

        Warning:
            |unstable|

        Note:
            |from_api| When your tournament is in a 'checking_in' or 'checked_in' state, there's no way to edit the tournament's start time (start_at) or check-in duration (check_in_duration). You must first abort check-in, then you may edit those attributes.
            1. Makes all participants active and clears their checked_in_at times.
            2. Transitions the tournament state from 'checking_in' or 'checked_in' to 'pending'

        Raises:
            APIException

        """
        params = {
                'include_participants': 1,  # forced to 1 since we need to update the Participant instances
                'include_matches': 1 if AUTO_GET_MATCHES else 0
            }
        res = await self.connection('POST', 'tournaments/{}/abort_check_in'.format(self._id), **params)
        self._refresh_from_json(res)

    async def get_final_ranking(self) -> OrderedDict:
        """ Get the ordered players ranking

        Returns:
            collections.OrderedDict[rank, List[Participant]]:

        Raises:
            APIException

        """
        if self._state != TournamentState.complete.value:
            return None

        ranking = {}
        for p in self.participants:
            if p.final_rank in ranking:
                ranking[p.final_rank].append(p)
            else:
                ranking[p.final_rank] = [p]

        return OrderedDict(sorted(ranking.items(), key=lambda t: t[0]))
