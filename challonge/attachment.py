from .helpers import FieldHolder


class Attachment(metaclass=FieldHolder):
    """ representation of a Challonge match attachment """

    _fields = ['id', 'match_id', 'user_id', 'description',
               'url', 'original_file_name', 'created_at',
               'updated_at', 'asset_file_name', 'asset_content_type',
               'asset_file_size', 'asset_url']

    def __init__(self, connection, json_def):
        self.connection = connection
        self._refresh_from_json(json_def)

    def _refresh_from_json(self, json_def):
        if 'match_attachment' in json_def:
            self._get_from_dict(json_def['match_attachment'])
