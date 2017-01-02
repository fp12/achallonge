from .helpers import FieldHolder


class Attachment(metaclass=FieldHolder):
    """ representation of a Challonge match attachment """

    _fields = ['id', 'match_id', 'user_id', 'description',
               'url', 'original_file_name', 'created_at',
               'updated_at', 'asset_file_name', 'asset_content_type',
               'asset_file_size', 'asset_url']

    def __init__(self, connection, json_def, **kwargs):
        self.connection = connection
        self._refresh_from_json(json_def)
        self._tournament_id = kwargs.get('tournament_id', 0)

    def _refresh_from_json(self, json_def):
        if 'match_attachment' in json_def:
            self._get_from_dict(json_def['match_attachment'])

    async def _change(self, url: str = None, description: str = None):
        assert (url is not None or description is not None), 'url:{} - description:{}'.format(url, description)
        params = {}
        if url is not None:
            params.update({'url': url})
        if description is not None:
            params.update({'description': description})
        res = await self.connection('PUT',
                                    'tournaments/{}/matches/{}/attachments/{}'.format(self._tournament_id, self._match_id, self._id),
                                    'match_attachment',
                                    **params)
        self._refresh_from_json(res)

    async def change_url(self, url: str, description: str = None):
        """ change the url of that attachment

        |methcoro|

        Args:
            url: url you want to change
            description: *optional* description for your attachment

        Raises:
            ChallongeException

        """
        await self._change(url, description)

    async def change_text(self, text: str):
        """ change the url of that attachment

        |methcoro|

        Args:
            text: content you want to add / modify (description)

        Raises:
            ChallongeException

        """
        await self._change(description=text)
