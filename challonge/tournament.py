from enum import Enum

from . import CHALLONGE_AUTO_GET_PARTICIPANTS, CHALLONGE_AUTO_GET_MATCHES
from .helpers import FieldHolder, get_from_dict, find_local
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

    def __init__(self, connection, json_def):
        self.connection = connection
        self.participants = None
        self.matches = None
        self._refresh_from_json(json_def)

    def _refresh_from_json(self, json_def):
        if 'tournament' in json_def:
            t_data = json_def['tournament']
            get_from_dict(self, t_data, *self._fields)
            if 'participants' in t_data:
                self.participants = [self._create_participant(p) for p in t_data['participants']]
            if 'matches' in t_data:
                self.matches = [self._create_match(m) for m in t_data['matches']]

    async def start(self):
        params = {
                'include_participants': 1 if CHALLONGE_AUTO_GET_PARTICIPANTS else 0,
                'include_matches': 1 if CHALLONGE_AUTO_GET_MATCHES else 0
            }
        res = await self.connection('POST', 'tournaments/{}/start'.format(self._id), **params)
        self._refresh_from_json(res)

    async def reset(self):
        params = {
                'include_participants': 1 if CHALLONGE_AUTO_GET_PARTICIPANTS else 0,
                'include_matches': 1 if CHALLONGE_AUTO_GET_MATCHES else 0
            }
        res = await self.connection('POST', 'tournaments/{}/reset'.format(self._id), **params)
        self._refresh_from_json(res)

    async def finalize(self):
        params = {
                'include_participants': 1 if CHALLONGE_AUTO_GET_PARTICIPANTS else 0,
                'include_matches': 1 if CHALLONGE_AUTO_GET_MATCHES else 0
            }
        res = await self.connection('POST', 'tournaments/{}/finalize'.format(self._id), **params)
        self._refresh_from_json(res)

    def _create_participant(self, json_def):
        return Participant(self.connection, json_def)

    def _add_participant(self, p: Participant):
        if p is not None:
            if self.participants is None:
                self.participants = []
            self.participants.append(p)

    async def get_participant(self, p_id: str, force_update=False) -> Participant:
        found_p = find_local(self.participants, p_id)
        if force_update or found_p is None:
            res = await self.connection('GET',
                                        'tournaments/{}/participants/{}'.format(self._id, p_id))
            found_p = self._create_participant(res)
            self._add_participant(found_p)
        return found_p

    async def get_participants(self, force_update=False) -> list:
        if force_update or self.participants is None:
            res = await self.connection('GET',
                                        'tournaments/{}/participants'.format(self._id))
            self.participants = [self._create_participant(p) for p in res]
        if self.participants is not None:
            return self.participants
        return []

    async def search_participant(self, name, force_update=False):
        if force_update or self.participants is None:
            self.get_participants()
        if self.participants is not None:
            for p in self.participants:
                if p.name == name:
                    return p
        return None

    async def add_participant(self, display_name: str = None, username: str = None, email: str = None, seed: int = 0, misc: str = None):
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

    async def add_participants(self, names: list) -> list:
        params = {'name': names}
        res = await self.connection('POST',
                                    'tournaments/{}/participants/bulk_add'.format(self._id),
                                    'participants[]',
                                    **params)
        self.participants = [self._create_participant(p) for p in res]
        if self.participants is not None:
            return self.participants
        return []

    async def remove_participant(self, p: Participant) -> list:
        await self.connection('DELETE',
                              'tournaments/{}/participants/{}'.format(self._id, p._id))
        return await self.get_participants(force_update=True)

    def _create_match(self, json_def):
        return Match(self.connection, json_def)

    def _add_match(self, p: Participant):
        if p is not None:
            if self.matches is None:
                self.matches = []
            self.matches.append(p)

    async def get_matches(self, force_update=False) -> list:
        if self._state != 'underway':
            print('tournament may not be started')
        if force_update or self.matches is None:
            res = await self.connection('GET',
                                        'tournaments/{}/matches'.format(self._id))
            self.matches = [self._create_match(m) for m in res]
        if self.matches is not None:
            return self.matches
        return []
