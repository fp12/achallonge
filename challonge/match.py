import re

from .helpers import FieldHolder, get_from_dict
from .participant import Participant


def verify_score_format(csv_score):
    result = re.compile('(\d+-\d+)(,\d+-\d+)*')
    return result.match(csv_score)


class Match(metaclass=FieldHolder):
    _fields = ['attachment_count', 'created_at', 'group_id', 'has_attachment',
               'id', 'identifier', 'location', 'loser_id', 'player1_id',
               'player1_is_prereq_match_loser', 'player1_prereq_match_id',
               'player1_votes', 'player2_id',
               'player2_is_prereq_match_loser', 'player2_prereq_match_id',
               'player2_votes', 'round', 'scheduled_time', 'started_at',
               'state', 'tournament_id', 'underway_at', 'updated_at',
               'winner_id', 'prerequisite_match_ids_csv', 'scores_csv']

    def __init__(self, connection, json_def):
        self.connection = connection
        self._refresh_from_json(json_def)

    def _refresh_from_json(self, json_def):
        if 'match' in json_def:
            get_from_dict(self, json_def['match'], *self._fields)

    async def _report(self, scores_csv, winner=None):
        if not verify_score_format(scores_csv):
            raise ValueError('Bad score format')
        params = {'scores_csv': scores_csv}
        if winner:
            params.update({'winner_id': winner})
        res = await self.connection('PUT',
                                    'tournaments/{}/matches/{}'.format(self._tournament_id, self._id),
                                    'match',
                                    **params)
        self._refresh_from_json(res)

    async def report_live_scores(self, scores_csv: str):
        await self._report(scores_csv)

    async def report_winner(self, winner: Participant, scores_csv: str):
        await self._report(scores_csv, winner._id)

    async def report_tie(self, scores_csv: str):
        await self._report(scores_csv, 'tie')
