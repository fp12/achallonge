import re

from .helpers import FieldHolder, assert_or_raise
from .participant import Participant
from .attachment import Attachment


def verify_score_format(csv_score):
    result = re.compile('(\d+-\d+)(,\d+-\d+)*')
    return result.match(csv_score)


class Match(metaclass=FieldHolder):
    """ Representation of a Challonge match """

    _fields = ['attachment_count', 'created_at', 'group_id', 'has_attachment',
               'id', 'identifier', 'location', 'loser_id', 'player1_id',
               'player1_is_prereq_match_loser', 'player1_prereq_match_id',
               'player1_votes', 'player2_id',
               'player2_is_prereq_match_loser', 'player2_prereq_match_id',
               'player2_votes', 'round', 'scheduled_time', 'started_at',
               'state', 'tournament_id', 'underway_at', 'updated_at',
               'winner_id', 'prerequisite_match_ids_csv', 'scores_csv',
               'optional', 'rushb_id', 'completed_at', 'suggested_play_order']

    def __init__(self, connection, json_def, tournament, **kwargs):
        self.connection = connection
        self._tournament = tournament

        self.attachments = None
        self._create_attachment = lambda a, **kwargs: self._create_holder(Attachment, a, **kwargs)

        self._refresh_from_json(json_def)

    def _refresh_from_json(self, json_def):
        if 'match' in json_def:
            m_data = json_def['match']
            self._get_from_dict(m_data)

            if 'attachments' in m_data:
                if self.attachments is None:
                    self.attachments = [self._create_attachment(a) for a in m_data['attachments']]
                else:
                    for a_data in m_data['attachments']:
                        for a in self.attachments:
                            if a_data['attachment']['id'] == a._id:
                                a._refresh_from_json(a_data)
                                break
                        else:
                            self.attachments.append(self._create_attachment(a_data))

    def _add_attachment(self, a: Attachment):
        if a is not None:
            if self.attachments is None:
                self.attachments = [a]
            else:
                self.attachments.append(a)

    async def _report(self, scores_csv, winner=None):
        assert_or_raise(verify_score_format(scores_csv), ValueError, 'Wrong score format')

        params = {'scores_csv': scores_csv}
        if winner:
            params.update({'winner_id': winner})
        res = await self.connection('PUT',
                                    'tournaments/{}/matches/{}'.format(self._tournament_id, self._id),
                                    'match',
                                    **params)
        self._refresh_from_json(res)
        # now we need to refresh all the matches of the tournament
        await self._tournament.get_matches(force_update=True)

    async def report_live_scores(self, scores_csv: str):
        """ report scores without giving a winner yet

        |methcoro|

        Args:
            scores_csv: Comma separated set/game scores with player 1 score first (e.g. "1-3,3-0,3-2")

        Raises:
            ValueError: scores_csv has a wrong format
            APIException

        """
        await self._report(scores_csv)

    async def report_winner(self, winner: Participant, scores_csv: str):
        """ report scores and give a winner

        |methcoro|

        Args:
            winner: :class:Participant instance
            scores_csv: Comma separated set/game scores with player 1 score first (e.g. "1-3,3-0,3-2")

        Raises:
            ValueError: scores_csv has a wrong format
            APIException

        """
        await self._report(scores_csv, winner._id)

    async def report_tie(self, scores_csv: str):
        """ report tie if applicable (Round Robin and Swiss)

        |methcoro|

        Args:
            scores_csv: Comma separated set/game scores with player 1 score first (e.g. "1-3,3-0,3-2")

        Raises:
            APIException

        """
        await self._report(scores_csv, 'tie')

    async def reopen(self):
        """ Reopens a match that was marked completed, automatically resetting matches that follow it

        |methcoro|

        Raises:
            APIException

        """
        res = await self.connection('POST', 'tournaments/{}/matches/{}/reopen'.format(self._tournament_id, self._id))
        self._refresh_from_json(res)
        
    async def mark_as_underway(self):
        """ Marks the match as underway

        |methcoro|

        Raises:
            APIException

        """
        res = await self.connection('POST', 'tournaments/{}/matches/{}/mark_as_underway'.format(self._tournament_id, self._id))
        self._refresh_from_json(res)

    async def unmark_as_underway(self):
        """ Unmarks the match as underway

        |methcoro|

        Raises:
            APIException

        """
        res = await self.connection('POST', 'tournaments/{}/matches/{}/unmark_as_underway'.format(self._tournament_id, self._id))
        self._refresh_from_json(res)

    async def change_votes(self, player1_votes: int = None, player2_votes: int = None, add: bool = False):
        """ change the votes for either player

        |methcoro|
        The votes will be overriden by default,
        If `add` is set to True, another API request call will be made to ensure the local is up to date with
        the Challonge server. Then the votes given in argument will be added to those on the server

        Args:
            player1_votes: if set, the player 1 votes will be changed to this value, or added to the current value if `add` is set
            player1_votes: if set, the player 2 votes will be changed to this value, or added to the current value if `add` is set
            add: if set, votes in parameters will be added instead of overriden

        Raises:
            ValueError: one of the votes arguments must not be None
            APIException

        """
        assert_or_raise(player1_votes is not None or player2_votes is not None,
                        ValueError,
                        'One of the votes must not be None')

        if add:
            # order a fresh update of this match
            res = await self.connection('GET', 'tournaments/{}/matches/{}'.format(self._tournament_id, self._id))
            self._refresh_from_json(res)
            if player1_votes is not None:
                player1_votes += self._player1_votes or 0
            if player2_votes is not None:
                player2_votes += self._player2_votes or 0

        params = {}
        if player1_votes is not None:
                params.update({'player1_votes': player1_votes})
        if player2_votes is not None:
                params.update({'player2_votes': player2_votes})
        res = await self.connection('PUT',
                                    'tournaments/{}/matches/{}'.format(self._tournament_id, self._id),
                                    'match',
                                    **params)
        self._refresh_from_json(res)

    async def _attach(self, asset=None, url: str = None, description: str = None):
        params = Attachment.prepare_params(asset, url, description)
        res = await self.connection('POST',
                                    'tournaments/{}/matches/{}/attachments'.format(self._tournament_id, self._id),
                                    'match_attachment',
                                    **params)
        new_a = self._create_attachment(res, tournament_id=self._tournament_id)
        self._add_attachment(new_a)
        return new_a

    async def attach_file(self, file_path: str, description: str = None) -> Attachment:
        """ add a file as an attachment

        |methcoro|

        Warning:
            |unstable|

        Args:
            file_path: path to the file you want to add
            description: *optional* description for your attachment

        Returns:
            Attachment:

        Raises:
            ValueError: file_path must not be None
            APIException

        """
        with open(file_path, 'rb') as f:
            return await self._attach(f.read(), description)

    async def attach_url(self, url: str, description: str = None) -> Attachment:
        """ add an url as an attachment

        |methcoro|

        Args:
            url: url you want to add
            description: *optional* description for your attachment

        Returns:
            Attachment:

        Raises:
            ValueError: url must not be None
            APIException

        """
        return await self._attach(url=url, description=description)

    async def attach_text(self, text: str) -> Attachment:
        """ add a simple text as an attachment

        |methcoro|

        Args:
            text: content you want to add (description)

        Returns:
            Attachment: newly created instance

        Raises:
            ValueError: text must not be None
            APIException

        """
        return await self._attach(description=text)

    async def destroy_attachment(self, a: Attachment):
        """ destroy a match attachment

        |methcoro|

        Args:
            a: the attachment you want to destroy

        Raises:
            APIException

        """
        await self.connection('DELETE', 'tournaments/{}/matches/{}/attachments/{}'.format(self._tournament_id, self._id, a._id))
        if a in self.attachments:
            self.attachments.remove(a)
