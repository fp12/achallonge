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
        return await self.connection('PUT',
                                     'tournaments/{}/participants/{}'.format(self._tournament_id, self._id),
                                     'participant',
                                     **params)

    async def change_display_name(self, new_name: str) -> str:
        """

        |methcoro|

        Note:
            |from_api| The name displayed in the bracket/schedule. Must be unique per tournament.

        Args:
            new_name: as described

        Returns:
            the same name as passed or `None` if something failed

        Raises:
            ChallongeException

        """
        res = await self._change(name=new_name)
        if 'participant' in res and 'name' in res['participant']:
            self._name = res['participant']['name']
            return self._name
        return None

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
        res = await self._change(seed=new_seed)
        if 'participant' in res and 'seed' in res['participant']:
            self._seed = res['participant']['seed']
            return self._seed
        return None

    async def change_misc(self, misc: str) -> str:
        """

        |methcoro|

        Note:
            |from_api| Max: 255 characters. Multi-purpose field that is only visible via the API and handy for site integration (e.g. key to your users table)

        Args:
            misc: str content

        Returns:
            the same seed number as passed or `None` if something failed

        Raises:
            ChallongeException

        """
        res = await self._change(misc=misc)
        if 'participant' in res and 'misc' in res['participant']:
            self._misc = res['participant']['misc']
            return self._misc
        return None

    async def check_in(self):
        res = await self.connection('POST',
                                    'tournaments/{}/participants/{}/check_in'.format(self._tournament_id, self._id),
                                    'participant')
        if 'participant' in res and 'checked_in_at' in res['participant']:
            self._checked_in_at = res['participant']['checked_in_at']
            return self._checked_in_at
        return None

    async def undo_check_in(self):
        res = await self.connection('POST',
                                    'tournaments/{}/participants/{}/undo_check_in'.format(self._tournament_id, self._id),
                                    'participant')
        if 'participant' in res and 'checked_in_at' in res['participant']:
            self._checked_in_at = res['participant']['checked_in_at']
            return self._checked_in_at
        return False
