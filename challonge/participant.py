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
               'can_check_in', 'checked_in', 'reactivatable']

    def __init__(self, connection, json_def, **kwargs):
        self.connection = connection
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
            ChallongeException

        """
        await self._change(name=new_name)

    async def change_username(self, username: str):
        """ will invite the Challonge user to the tournament

        |methcoro|

        Args:
            username: Challonge username

        Raises:
            ChallongeException

        """
        await self._change(challonge_username=username)

    async def change_email(self, email: str):
        """  set / update the email associated to the participant

        |methcoro|

        Setting an email will first search for a matching Challonge account.
        If one is found, it will be invited to the tournament.
        If one is not found, the "new-user-email" attribute will be set, and the user will be invited via email to create an account.

        Args:
            email: as described

        Raises:
            ChallongeException

        """
        await self._change(email=email)

    async def change_seed(self, new_seed: int) -> int:
        """

        |methcoro|

        Note:
            |from_api| Must be between 1 and the current number of participants (including the new record). Overwriting an existing seed will automatically bump other participants as you would expect.

        Args:
            new_seed: as described

        Returns:
            the same seed number as passed or `None` if something failed

        Raises:
            ChallongeException

        """
        await self._change(seed=new_seed)

    async def change_misc(self, misc: str) -> str:
        """
        |methcoro|

        Note:
            |from_api| Max: 255 characters. Multi-purpose field that is only visible via the API and handy for site integration (e.g. key to your users table)

        Args:
            misc: str content

        Raises:
            ChallongeException

        """
        await self._change(misc=misc)

    async def check_in(self):
        """

        |methcoro|

        Warning:
            |unstable|

        Raises:
            ChallongeException

        """
        res = await self.connection('POST', 'tournaments/{}/participants/{}/check_in'.format(self._tournament_id, self._id))
        self._refresh_from_json(res)

    async def undo_check_in(self):
        """
        |methcoro|

        Warning:
            |unstable|

        Raises:
            ChallongeException

        """
        res = await self.connection('POST', 'tournaments/{}/participants/{}/undo_check_in'.format(self._tournament_id, self._id))
        self._refresh_from_json(res)
