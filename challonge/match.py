import re

from .helpers import FieldHolder
from .participant import Participant
from .attachment import Attachment


def verify_score_format(csv_score):
    result = re.compile('(\d+-\d+)(,\d+-\d+)*')
    return result.match(csv_score)


class Match(metaclass=FieldHolder):
    """ representation of a Challonge match """

    _fields = ['attachment_count', 'created_at', 'group_id', 'has_attachment',
               'id', 'identifier', 'location', 'loser_id', 'player1_id',
               'player1_is_prereq_match_loser', 'player1_prereq_match_id',
               'player1_votes', 'player2_id',
               'player2_is_prereq_match_loser', 'player2_prereq_match_id',
               'player2_votes', 'round', 'scheduled_time', 'started_at',
               'state', 'tournament_id', 'underway_at', 'updated_at',
               'winner_id', 'prerequisite_match_ids_csv', 'scores_csv']

    def __init__(self, connection, json_def, **kwargs):
        self.connection = connection

        self.attachments = None
        self._create_attachment = lambda a, **kwargs: self._create_holder(Attachment, a, **kwargs)

        self._refresh_from_json(json_def)

    def _refresh_from_json(self, json_def):
        if 'match' in json_def:
            self._get_from_dict(json_def['match'])

    def _add_attachment(self, a: Attachment):
        if a is not None:
            if self.attachments is None:
                self.attachments = [a]
            else:
                self.attachments.append(a)

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
        """ report scores without giving a winner yet

        |methcoro|

        Args:
            scores_csv: Comma separated set/game scores with player 1 score first (e.g. "1-3,3-0,3-2")

        Raises:
            ChallongeException

        """
        await self._report(scores_csv)

    async def report_winner(self, winner: Participant, scores_csv: str):
        """ report scores and give a winner

        |methcoro|

        Args:
            winner: :class:Participant instance
            scores_csv: Comma separated set/game scores with player 1 score first (e.g. "1-3,3-0,3-2")

        Raises:
            ChallongeException

        """
        await self._report(scores_csv, winner._id)

    async def report_tie(self, scores_csv: str):
        """ report tie if applicable (Round Robin and Swiss)

        |methcoro|

        Args:
            scores_csv: Comma separated set/game scores with player 1 score first (e.g. "1-3,3-0,3-2")

        Raises:
            ChallongeException

        """
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
        new_a = self._create_attachment(res, tournament_id=self._tournament_id)
        self._add_attachment(new_a)
        return new_a

    async def attach_url(self, url: str, description: str = None) -> Attachment:
        """ add an url as an attachment

        |methcoro|

        Args:
            url: url you want to add
            description: *optional* description for your attachment

        Returns:
            Attachment:

        Raises:
            ChallongeException

        """
        return await self._attach(url, description)

    async def attach_text(self, text: str) -> Attachment:
        """ add a simple text as an attachment

        |methcoro|

        Args:
            text: content you want to add (description)

        Returns:
            Attachment: newly created instance

        Raises:
            ChallongeException

        """
        return await self._attach(description=text)

    async def destroy_attachment(self, a: Attachment):
        """ destroy a match attachment

        |methcoro|

        Args:
            a: the attachment your want to destroy

        Raises:
            ChallongeException

        """
        await self.connection('DELETE', 'tournaments/{}/matches/{}/attachments/{}'.format(self._tournament_id, self._id, a._id))
        if a in self.attachments:
            self.attachments.remove(a)
        else:
            # TODO: error management
            pass
