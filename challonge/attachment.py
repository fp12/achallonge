from .helpers import FieldHolder, assert_or_raise


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

    @staticmethod
    def prepare_params(asset, url: str, description: str):
        assert_or_raise(asset is not None or url is not None or description is not None,
                        ValueError,
                        'One of the following must not be None: asset, url, description')
        params = {}
        if asset is not None:
            params.update({'asset': asset})
        elif url is not None:
            params.update({'url': url})
        if description is not None:
            params.update({'description': description})
        return params

    async def _change(self, asset=None, url: str = None, description: str = None):
        params = Attachment.prepare_params(asset, url, description)
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
            ValueError: url must not be None
            APIException

        """
        await self._change(url=url, description=description)

    async def change_text(self, text: str):
        """ change the text / description of that attachment

        |methcoro|

        Args:
            text: content you want to add / modify (description)

        Raises:
            ValueError: text must not be None
            APIException

        """
        await self._change(description=text)

    change_description = change_text

    async def change_file(self, file_path: str, description: str = None):
        """ change the file of that attachment

        |methcoro|

        Warning:
            |unstable|

        Args:
            file_path: path to the file you want to add / modify
            description: *optional* description for your attachment

        Raises:
            ValueError: file_path must not be None
            APIException

        """
        with open(file_path, 'rb') as f:
            await self._change(asset=f.read())
