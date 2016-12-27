import re

from .helpers import FieldHolder, get_from_dict
from .participant import Participant
from .attachment import Attachment


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

        self.attachments = None
        self._create_attachment = lambda a: self._create_holder(Attachment, a)
        self._add_attachment = lambda a: self._add_holder(self.attachments, a)

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

    async def _attach(self, url: str = None, description: str = None):
        assert (url is not None or description is not None), 'url:{} - description:{}'.format(url, description)
        params = {'description': description or ''}
        if url is not None:
            params.update({'url': url})
        res = await self.connection('POST',
                                    'tournaments/{}/matches/{}/attachments'.format(self._tournament_id, self._id),
                                    'match_attachment',
                                    **params)
        new_a = self._create_attachment(res)
        self._add_attachment(new_a)
        return new_a

    async def attach_url(self, url: str, description: str = None) -> Attachment:
        return await self._attach(url, description)

    async def attach_text(self, text: str = None) -> Attachment:
        return await self._attach(description=text)
