from . import AUTO_GET_PARTICIPANTS, AUTO_GET_MATCHES
from .helpers import get_connection
from .tournament import Tournament, TournamentType


class User:
    """ Representation of a Challonge user

    Main entry point for using the async challonge library.

    """

    def __init__(self, username: str, api_key: str, **kwargs):
        self.tournaments = None
        self.connection = get_connection(username, api_key, **kwargs)

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

    def _find_tournament(self, e_id):
        if self.tournaments is not None:
            for e in self.tournaments:
                if e.id == int(e_id):
                    return e
        return None

    async def validate(self):
        """ checks whether the current user is connected

        |methcoro|

        Raises:
            APIException

        """
        await self.connection('GET', 'tournaments')

    async def get_tournament(self, t_id: int, force_update=False) -> Tournament:
        """ gets a tournament with its id

        |methcoro|

        Args:
            t_id: tournament id
            force_update: *optional* set to True to force the data update from Challonge

        Returns:
            Tournament

        Raises:
            APIException

        """
        found_t = self._find_tournament(t_id)
        if force_update or found_t is None:
            res = await self.connection('GET', 'tournaments/{}'.format(t_id))
            self._refresh_tournament_from_json(res)
            found_t = self._find_tournament(t_id)

        return found_t

    async def get_tournaments(self, force_update=False) -> list:
        """ gets all user's tournaments

        |methcoro|

        Args:
            force_update: *optional* set to True to force the data update from Challonge

        Returns:
            list[Tournament]: list of all the user tournaments

        Raises:
            APIException

        """
        if force_update or self.tournaments is None:
            params = {
                'include_participants': 1 if AUTO_GET_PARTICIPANTS else 0,
                'include_matches': 1 if AUTO_GET_MATCHES else 0
            }
            res = await self.connection('GET', 'tournaments', **params)
            if len(res) == 0:
                self.tournaments = []
            else:
                for t_data in res:
                    self._refresh_tournament_from_json(t_data)

        return self.tournaments

    async def create_tournament(self, name: str, url: str, tournament_type=TournamentType.single_elimination, **params) -> Tournament:
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
        return self._find_tournament(res['tournament']['id'])

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
