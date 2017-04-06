from .helpers import FieldHolder


class Participant(metaclass=FieldHolder):
    """ representation of a Challonge participant """

    _fields = ['active', 'checked_in_at', 'created_at', 'final_rank',
               'group_id', 'icon', 'id', 'invitation_id', 'invite_email',
               'misc', 'name', 'on_waiting_list', 'seed', 'tournament_id',
               'updated_at', 'challonge_username', 'challonge_email_address_verified',
               'removable', 'participatable_or_invitation_attached', 'confirm_remove',
               'invitation_pending', 'display_name_with_invitation_email_address',
               'email_hash', 'username', 'attached_participatable_portrait_url',
               'can_check_in', 'checked_in', 'reactivatable',
               'display_name', 'group_player_ids']

    def __init__(self, connection, json_def, tournament, **kwargs):
        self.connection = connection
        self._tournament = tournament
        self._refresh_from_json(json_def)

    def _refresh_from_json(self, json_def):
        if 'participant' in json_def:
            self._get_from_dict(json_def['participant'])

    async def _change(self, **params):
        res = await self.connection('PUT',
                                    'tournaments/{}/participants/{}'.format(self._tournament_id, self._id),
                                    'participant',
                                    **params)
        self._refresh_from_json(res)

    async def change_display_name(self, new_name: str):
        """ Change the name displayed on the Challonge website

        |methcoro|

        Note:
            |from_api| The name displayed in the bracket/schedule. Must be unique per tournament.

        Args:
            new_name: as described

        Raises:
            APIException

        """
        await self._change(name=new_name)

    async def change_username(self, username: str):
        """ Will invite the Challonge user to the tournament

        |methcoro|

        Args:
            username: Challonge username

        Raises:
            APIException

        """
        await self._change(challonge_username=username)

    async def change_email(self, email: str):
        """  Set / update the email associated to the participant

        |methcoro|

        Setting an email will first search for a matching Challonge account.
        If one is found, it will be invited to the tournament.
        If one is not found, the "new-user-email" attribute will be set, and the user will be invited via email to create an account.

        Args:
            email: as described

        Raises:
            APIException

        """
        await self._change(email=email)

    async def change_seed(self, new_seed: int) -> int:
        """ Change the seed of the participant

        |methcoro|

        Note:
            |from_api| Must be between 1 and the current number of participants (including the new record). Overwriting an existing seed will automatically bump other participants as you would expect.

        Args:
            new_seed: as described

        Returns:
            the same seed number as passed or `None` if something failed

        Raises:
            APIException

        """
        await self._change(seed=new_seed)

    async def change_misc(self, misc: str) -> str:
        """ Change the `misc` field

        |methcoro|

        Note:
            |from_api| Max: 255 characters. Multi-purpose field that is only visible via the API and handy for site integration (e.g. key to your users table)

        Args:
            misc: str content

        Raises:
            APIException

        """
        await self._change(misc=misc)

    async def check_in(self):
        """ Checks this participant in

        |methcoro|

        Warning:
            |unstable|

        Raises:
            APIException

        """
        res = await self.connection('POST', 'tournaments/{}/participants/{}/check_in'.format(self._tournament_id, self._id))
        self._refresh_from_json(res)

    async def undo_check_in(self):
        """ Undo the check in for this participant

        |methcoro|

        Warning:
            |unstable|

        Raises:
            APIException

        """
        res = await self.connection('POST', 'tournaments/{}/participants/{}/undo_check_in'.format(self._tournament_id, self._id))
        self._refresh_from_json(res)

    async def get_next_match(self):
        """ Return the first open match found, or if none, the first pending match found

        |methcoro|

        Raises:
            APIException

        """
        if self._final_rank is not None:
            return None

        open_matches = await self.connection('GET',
                                             'tournaments/{}/matches'.format(self._tournament_id),
                                             state='open',
                                             participant_id=self._id)
        if len(open_matches) > 0:
            return await self._tournament.get_match(open_matches[0]['match']['id'])

        pending_matches = await self.connection('GET',
                                                'tournaments/{}/matches'.format(self._tournament_id),
                                                state='pending',
                                                participant_id=self._id)
        if len(pending_matches) > 0:
            return await self._tournament.get_match(pending_matches[0]['match']['id'])

        return None

    async def get_next_opponent(self):
        """ Get the opponent of the potential next match. See :func:`get_next_match`

        |methcoro|

        Raises:
            APIException

        """
        next_match = await self.get_next_match()
        if next_match is not None:
            opponent_id = next_match.player1_id if next_match.player2_id == self._id else next_match.player2_id
            return await self._tournament.get_participant(opponent_id)
        return None
