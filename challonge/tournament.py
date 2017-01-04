from datetime import datetime
from enum import Enum

from . import CHALLONGE_AUTO_GET_PARTICIPANTS, CHALLONGE_AUTO_GET_MATCHES
from .helpers import FieldHolder
from .participant import Participant
from .match import Match


class TournamentType(Enum):
    single_elimination = 'single elimination'
    double_elimination = 'double elimination'
    round_robin = 'round robin'
    swiss = 'swiss'


class TournamentState(Enum):
    pending = 0
    open = 1
    complete = 2
    in_progress = 3


class TournamentStateResult(Enum):
    underway = 0
    pending = 1


class Tournament(metaclass=FieldHolder):
    """ representation of a Challonge tournament """

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
               'ranked_by', 'require_shelpers_agreement',
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
               'team_convertable', 'group_stages_were_started']

    def __init__(self, connection, json_def, **kwargs):
        self.connection = connection

        self.participants = None
        self._create_participant = lambda p: self._create_holder(Participant, p)
        self._find_participant = lambda p_id: self._find_holder(self.participants, p_id)

        self.matches = None
        self._create_match = lambda m: self._create_holder(Match, m)

        self._refresh_from_json(json_def)

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
            ChallongeException

        """
        params = {
                'include_participants': 1 if CHALLONGE_AUTO_GET_PARTICIPANTS else 0,
                'include_matches': 1 if CHALLONGE_AUTO_GET_MATCHES else 0
            }
        res = await self.connection('POST', 'tournaments/{}/start'.format(self._id), **params)
        self._refresh_from_json(res)

    async def reset(self):
        """ reset the tournament on Challonge

        |methcoro|

        Note:
            |from_api| Reset a tournament, clearing all of its scores and attachments. You can then add/remove/edit participants before starting the tournament again.

        Raises:
            ChallongeException

        """
        params = {
                'include_participants': 1 if CHALLONGE_AUTO_GET_PARTICIPANTS else 0,
                'include_matches': 1 if CHALLONGE_AUTO_GET_MATCHES else 0
            }
        res = await self.connection('POST', 'tournaments/{}/reset'.format(self._id), **params)
        self._refresh_from_json(res)

    async def finalize(self):
        """ finalize the tournament on Challonge

        |methcoro|

        Note:
            |from_api| Finalize a tournament that has had all match scores submitted, rendering its results permanent.

        Raises:
            ChallongeException

        """
        params = {
                'include_participants': 1 if CHALLONGE_AUTO_GET_PARTICIPANTS else 0,
                'include_matches': 1 if CHALLONGE_AUTO_GET_MATCHES else 0
            }
        res = await self.connection('POST', 'tournaments/{}/finalize'.format(self._id), **params)
        self._refresh_from_json(res)

    async def allow_attachments(self, allow: bool = True):
        """ allow this tournament to accept attachments or not

        |methcoro|

        Args:
            allow (default=True): False to disallow

        Raises:
            ChallongeException

        """
        res = await self.connection('PUT',
                                    'tournaments/{}'.format(self._id),
                                    'tournament',
                                    accept_attachments=allow)
        self._refresh_from_json(res)

    async def set_start_date(self, date: str, time: str, check_in_duration: int = None):
        """ set the tournament start date (and check in duration)

        |methcoro|

        Args:
            date: fomatted date as YYYY/MM/DD (2017/02/14)
            time: fromatted time as HH:MM (20:15)
            check_in_duration (optional): duration in minutes

        Raises:
            ChallongeException

        """
        date_time = datetime.strptime(date + ' ' + time, '%Y/%m/%d %H:%M')
        res = await self.connection('PUT',
                                    'tournaments/{}'.format(self._id),
                                    'tournament',
                                    start_at=date_time,
                                    check_in_duration=check_in_duration or 0)
        self._refresh_from_json(res)

    async def get_participant(self, p_id: int, force_update=False) -> Participant:
        """ get a participant by its id

        |methcoro|

        Args:
            p_id: participant id
            force_update (dfault=False): True to force an update to the Challonge API

        Returns:
            Participant: None if not found

        Raises:
            ChallongeException

        """
        found_p = self._find_participant(p_id)
        if force_update or found_p is None:
            res = await self.connection('GET', 'tournaments/{}/participants/{}'.format(self._id, p_id))
            found_p._refresh_from_json(res)
        return found_p

    async def get_participants(self, force_update=False) -> list:
        """ get all participants

        |methcoro|

        Args:
            force_update (default=False): True to force an update to the Challonge API

        Returns:
            list[Participant]:

        Raises:
            ChallongeException

        """
        if force_update or self.participants is None:
            res = await self.connection('GET',
                                        'tournaments/{}/participants'.format(self._id))
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
            ChallongeException

        """
        if force_update or self.participants is None:
            self.get_participants()
        if self.participants is not None:
            for p in self.participants:
                if p.name == name:
                    return p
        return None

    async def add_participant(self, display_name: str = None, username: str = None, email: str = None, seed: int = 0, misc: str = None):
        """ add a participant to the tournament

        |methcoro|

        Args:
            display_name: The name displayed in the bracket/schedule - not required if email or challonge_username is provided. Must be unique per tournament.
            username: Provide this if the participant has a Challonge account. He or she will be invited to the tournament.
            email: Providing this will first search for a matching Challonge account. If one is found, this will have the same effect as the "challonge_username" attribute. If one is not found, the "new-user-email" attribute will be set, and the user will be invited via email to create an account.
            seed: The participant's new seed. Must be between 1 and the current number of participants (including the new record). Overwriting an existing seed will automatically bump other participants as you would expect.
            misc: Max: 255 characters. Multi-purpose field that is only visible via the API and handy for site integration (e.g. key to your users table)

        Returns:
            Participant: newly created participant

        Raises:
            ChallongeException

        """
        assert((display_name is None) ^ (username is None))
        params = {
            'name': display_name or '',
            'challonge_username': username or '',
        }
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

    # not documented because may need to be improved
    async def add_participants(self, *names: str) -> list:
        params = {'name': list(names)}
        res = await self.connection('POST',
                                    'tournaments/{}/participants/bulk_add'.format(self._id),
                                    'participants[]',
                                    **params)
        self._refresh_participants_from_json(res)
        return self.participants

    async def remove_participant(self, p: Participant):
        """ remove a participant from the tournament

        |methcoro|

        Args:
            p: the participant to remove

        Raises:
            ChallongeException

        """
        await self.connection('DELETE', 'tournaments/{}/participants/{}'.format(self._id, p._id))
        if p in self.participants:
            self.participants.remove(p)
        else:
            # TODO: error management
            pass

    async def get_matches(self, force_update=False) -> list:
        """ get all matches (once the tournament is started)

        |methcoro|

        Args:
            force_update (default=False): True to force an update to the Challonge API

        Returns:
            list[Match]:

        Raises:
            ChallongeException

        """
        if self._state != 'underway':
            print('tournament may not be started')

        if force_update or self.matches is None:
            params = {'include_attachments': 1}
            res = await self.connection('GET',
                                        'tournaments/{}/matches'.format(self._id),
                                        **params)
            self._refresh_matches_from_json(res)
        return self.matches or []

    async def process_check_ins(self):
        """ finalize the check in phase

        |methcoro|

        Notes:
            |from_api| This should be invoked after a tournament's check-in window closes before the tournament is started.
            1. Marks participants who have not checked in as inactive.
            2. Moves inactive participants to bottom seeds (ordered by original seed).
            3. Transitions the tournament state from 'checking_in' to 'checked_in'
            NOTE: Checked in participants on the waiting list will be promoted if slots become available.

        Raises:
            ChallongeException

        """
        params = {
                'include_participants': 1,  # forced to 1 since we need to update the Participant instances
                'include_matches': 1 if CHALLONGE_AUTO_GET_MATCHES else 0
            }
        res = await self.connection('POST', 'tournaments/{}/process_check_ins'.format(self._id), **params)
        self._refresh_from_json(res)

    async def abort_check_in(self):
        """ abort the check in process

        |methcoro|

        Notes:
            |from_api| When your tournament is in a 'checking_in' or 'checked_in' state, there's no way to edit the tournament's start time (start_at) or check-in duration (check_in_duration). You must first abort check-in, then you may edit those attributes.
            1. Makes all participants active and clears their checked_in_at times.
            2. Transitions the tournament state from 'checking_in' or 'checked_in' to 'pending'

        Raises:
            ChallongeException

        """
        params = {
                'include_participants': 1,  # forced to 1 since we need to update the Participant instances
                'include_matches': 1 if CHALLONGE_AUTO_GET_MATCHES else 0
            }
        res = await self.connection('POST', 'tournaments/{}/abort_check_in'.format(self._id), **params)
        self._refresh_from_json(res)
