from .helpers import FieldHolder, get_from_dict


class Participant(metaclass=FieldHolder):
    _fields = ['active', 'checked_in_at', 'created_at', 'final_rank',
               'group_id', 'icon', 'id', 'invitation_id', 'invite_email',
               'misc', 'name', 'on_waiting_list', 'seed', 'tournament_id',
               'updated_at', 'challonge_username', 'challonge_email_address_verified',
               'removable', 'participatable_or_invitation_attached', 'confirm_remove',
               'invitation_pending', 'display_name_with_invitation_email_address',
               'email_hash', 'username', 'attached_participatable_portrait_url',
               'can_check_in', 'checked_in', 'reactivatable']

    def __init__(self, connection, json_def):
        self.connection = connection
        self._refresh_from_json(json_def)

    def _refresh_from_json(self, json_def):
        if 'participant' in json_def:
            get_from_dict(self, json_def['participant'], *self._fields)

    async def change_display_name(self, new_name: str) -> str:
        res = await self.connection('PUT',
                                    'tournaments/{}/participants/{}'.format(self._tournament_id, self._id),
                                    'participant',
                                    name=new_name)
        if 'participant' in res and 'name' in res['participant']:
            self._name = res['participant']['name']
            return self._name
        return None

    async def change_seed(self, new_seed: int) -> int:
        res = await self.connection('PUT',
                                    'tournaments/{}/participants/{}'.format(self._tournament_id, self._id),
                                    'participant',
                                    seed=new_seed)
        if 'participant' in res and 'seed' in res['participant']:
            self._seed = res['participant']['seed']
            return self._seed
        return None

    async def change_misc(self, misc: str) -> str:
        res = await self.connection('PUT',
                                    'tournaments/{}/participants/{}'.format(self._tournament_id, self._id),
                                    'participant',
                                    misc=misc)
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
