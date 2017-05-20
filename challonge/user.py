from . import AUTO_GET_PARTICIPANTS, AUTO_GET_MATCHES
from .helpers import get_connection, assert_or_raise
from .tournament import Tournament, TournamentType


class User:
    """ Representation of a Challonge user

    Main entry point for using the async challonge library.

    """

    def __init__(self, username: str, api_key: str, **kwargs):
        self.tournaments = None
        self.connection = get_connection(username, api_key, **kwargs)
        self._subdomains_searched = []

    def _refresh_tournament_from_json(self, tournament_data):
        if self.tournaments is None:
            self.tournaments = [self._create_tournament(tournament_data)]
        else:
            for t in self.tournaments:
                if tournament_data['tournament']['id'] == t._id:
                    t._refresh_from_json(tournament_data)
                    break
            else:
                self.tournaments.append(self._create_tournament(tournament_data))

    def _create_tournament(self, json_def) -> Tournament:
        return Tournament(self.connection, json_def)

    def _find_tournament_by_id(self, e_id):
        if self.tournaments is not None:
            for e in self.tournaments:
                if e.id == int(e_id):
                    return e
        return None

    def _find_tournament_by_url(self, url, subdomain):
        if self.tournaments is not None:
            for e in self.tournaments:
                if e.url == url:
                    if subdomain is None or e.subdomain == subdomain:
                        return e
        return None

    async def validate(self):
        """ checks whether the current user is connected

        |methcoro|

        Raises:
            APIException

        """
        await self.connection('GET', 'tournaments')

    async def get_tournament(self, t_id: int = None, url: str = None, subdomain: str = None, force_update=False) -> Tournament:
        """ gets a tournament with its id or url or url+subdomain
        Note: from the API, it can't be known if the retrieved tournament was made from this user.
        Thus, any tournament  is added to the local list of tournaments, but some functions (updates/destroy...) cannot be used for tournaments not owned by this user.

        |methcoro|

        Args:
            t_id: tournament id
            url: last part of the tournament url (http://challonge.com/XXX)
            subdomain: first part of the tournament url, if any (http://XXX.challonge.com/...)
            force_update: *optional* set to True to force the data update from Challonge

        Returns:
            Tournament

        Raises:
            APIException
            ValueError: if neither of the arguments are provided

        """
        assert_or_raise((t_id is None) ^ (url is None),
                        ValueError,
                        'One of t_id or url must not be None')

        found_t = self._find_tournament_by_id(t_id) if t_id is not None else self._find_tournament_by_url(url, subdomain)
        if force_update or found_t is None:
            param = t_id
            if param is None:
                if subdomain is not None:
                    param = '{}-{}'.format(subdomain, url)
                else:
                    param = url
            res = await self.connection('GET', 'tournaments/{}'.format(param))
            self._refresh_tournament_from_json(res)
            found_t = self._find_tournament_by_id(res['tournament']['id'])

        return found_t

    async def get_tournaments(self, subdomain: str = None, force_update: bool = False) -> list:
        """ gets all user's tournaments

        |methcoro|

        Args:
            subdomain: *optional* subdomain needs to be given explicitely to get tournaments in a subdomain
            force_update: *optional* set to True to force the data update from Challonge

        Returns:
            list[Tournament]: list of all the user tournaments

        Raises:
            APIException

        """
        if self.tournaments is None:
            force_update = True
            self._subdomains_searched.append('' if subdomain is None else subdomain)
        elif subdomain is None and '' not in self._subdomains_searched:
            force_update = True
            self._subdomains_searched.append('')
        elif subdomain is not None and subdomain not in self._subdomains_searched:
            force_update = True
            self._subdomains_searched.append(subdomain)

        if force_update:
            params = {
                'include_participants': 1 if AUTO_GET_PARTICIPANTS else 0,
                'include_matches': 1 if AUTO_GET_MATCHES else 0
            }
            if subdomain is not None:
                params['subdomain'] = subdomain

            res = await self.connection('GET', 'tournaments', **params)
            if len(res) == 0:
                self.tournaments = []
            else:
                for t_data in res:
                    self._refresh_tournament_from_json(t_data)

        return self.tournaments

    async def create_tournament(self, name: str, url: str, tournament_type: TournamentType = TournamentType.single_elimination, **params) -> Tournament:
        """ creates a simple tournament with basic options

        |methcoro|

        Args:
            name: name of the new tournament
            url: url of the new tournament (http://challonge.com/url)
            tournament_type: Defaults to TournamentType.single_elimination
            params: optional params (see http://api.challonge.com/v1/documents/tournaments/create)

        Returns:
            Tournament: the newly created tournament

        Raises:
            APIException

        """
        params.update({
            'name': name,
            'url': url,
            'tournament_type': tournament_type.value,
        })
        res = await self.connection('POST', 'tournaments', 'tournament', **params)
        self._refresh_tournament_from_json(res)
        return self._find_tournament_by_id(res['tournament']['id'])

    async def destroy_tournament(self, t: Tournament):
        """ completely removes a tournament from Challonge

        |methcoro|

        Note:
            |from_api| Deletes a tournament along with all its associated records. There is no undo, so use with care!

        Raises:
            APIException

        """
        await self.connection('DELETE', 'tournaments/{}'.format(t.id))
        if t in self.tournaments:
            self.tournaments.remove(t)


async def get_user(username: str, api_key: str, **kwargs) -> User:
    """ Creates a new user, validate its credentials and returns it

    |funccoro|

    Args:
        username: username as specified on the challonge website
        api_key: key as found on the challonge
            `settings <https://challonge.com/settings/developer>`_

    Returns:
        User: a logged in user if no exception has been raised

    Raises:
        APIException

    """
    new_user = User(username, api_key, **kwargs)
    await new_user.validate()
    return new_user
