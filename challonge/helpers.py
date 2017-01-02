import aiohttp

from . import CHALLONGE_USE_FIELDS_DESCRIPTORS


DEFAULT_TIMEOUT = 30


class ChallongeException(Exception):
    """ If anything goes wrong during the request to the Challonge API, this exception will be raised """
    pass


class FieldDescriptor:
    def __init__(self, attr):
        self.attr = attr
        self.__doc__ = 'readonly attribute'

    def __get__(self, instance, owner):
        return getattr(instance, self.attr) if instance else self


class FieldHolder(type):
    private_name = '_{}'

    def _create_holder(self, holder_class, json_def, **kwargs):
        return holder_class(self.connection, json_def, **kwargs)

    def _find_holder(self, local_list, e_id):
        if local_list is not None:
            for e in local_list:
                if e.id == int(e_id):
                    return e
        return None

    def _get_from_dict(self, data):
        for a in self._fields:
            name = FieldHolder.private_name.format(a) if CHALLONGE_USE_FIELDS_DESCRIPTORS else a
            setattr(self, name, data[a] if a in data else None)

    def __init__(cls, name, bases, dct):
        super(FieldHolder, cls).__init__(name, bases, dct)

        cls._create_holder = FieldHolder._create_holder
        cls._find_holder = FieldHolder._find_holder
        cls._get_from_dict = FieldHolder._get_from_dict

        if CHALLONGE_USE_FIELDS_DESCRIPTORS:
            for a in cls._fields:
                setattr(cls, a, FieldDescriptor(FieldHolder.private_name.format(a)))


class Connection:
    challonge_api_url = 'https://api.challonge.com/v1/{}.json'

    def __init__(self, username: str, api_key: str, timeout, loop):
        self.username = username
        self.api_key = api_key
        self.timeout = timeout
        self.loop = loop

    async def __call__(self, method: str, uri: str, params_prefix: str =None, **params):
        params = self._prepare_params(params, params_prefix)
        # print(params)

        # build the HTTP request and use basic authentication
        url = self.challonge_api_url.format(uri)

        async with aiohttp.ClientSession(loop=self.loop) as session:
            with aiohttp.Timeout(self.timeout):
                auth = aiohttp.BasicAuth(login=self.username, password=self.api_key)
                async with session.request(method, url, params=params, auth=auth) as response:
                    resp = await response.json()
                    if response.status >= 400:
                        raise ChallongeException(uri, params, response.reason)
                    return resp
        return None

    @staticmethod
    def _prepare_params(params, prefix=None) -> dict:
        def val(value):
            if isinstance(value, bool):
                # challonge only accepts lowercase true/false
                value = str(value).lower()
            return str(value)

        new_params = []
        if prefix:
            if prefix.endswith('[]'):
                for k, v in params.items():
                    new_params.extend([('{}[{}]'.format(prefix, k), val(u)) for u in v])
            else:
                new_params = [('{}[{}]'.format(prefix, k), val(v)) for k, v in params.items()]
        else:
            new_params = [(k, val(v)) for k, v in params.items()]
        return new_params


def get_connection(username, api_key, timeout=DEFAULT_TIMEOUT, loop=None):
    return Connection(username, api_key, timeout, loop)
