from . import CHALLONGE_AUTO_GET_PARTICIPANTS, CHALLONGE_AUTO_GET_MATCHES
from .helpers import get_connection, find_local
from .tournament import Tournament, TournamentType


class User:
    """ representation of a Challonge user

    Main entry point for using the async challonge library.

    """

    def __init__(self, username: str, api_key: str, **kwargs):
        self.tournaments = None
        self.connection = get_connection(username, api_key, **kwargs)

    def _add_tournament(self, t: Tournament):
        if t is not None:
            if self.tournaments is None:
                self.tournaments = []
            self.tournaments.append(t)

    def _create_tournament(self, json_def) -> Tournament:
        return Tournament(self.connection, json_def)

    async def validate(self):
        """ checks whether the current user is connected

        |methcoro|

        Raises:
            ChallongeException

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
            ChallongeException

        """
        found_t = find_local(self.tournaments, t_id)
        if force_update or found_t is None:
            res = await self.connection('GET', 'tournaments/{}'.format(t_id))
            found_t = self._create_tournament(res)
            self._add_tournament(found_t)
        return found_t

    async def get_tournaments(self, force_update=False) -> list:
        """ gets all user's tournaments

        |methcoro|

        Args:
            force_update: *optional* set to True to force the data update from Challonge

        Returns:
            list[Tournament]: list of all the user tournaments

        Raises:
            ChallongeException

        """
        if force_update or self.tournaments is None:
            params = {
                'include_participants': 1 if CHALLONGE_AUTO_GET_PARTICIPANTS else 0,
                'include_matches': 1 if CHALLONGE_AUTO_GET_MATCHES else 0
            }
            res = await self.connection('GET', 'tournaments', **params)
            self.tournaments = [self._create_tournament(t) for t in res]
        if self.tournaments is not None:
            return self.tournaments
        return []

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
            ChallongeException

        """
        params.update({
            'name': name,
            'url': url,
            'tournament_type': tournament_type.value,
        })
        res = await self.connection('POST', 'tournaments', 'tournament', **params)
        new_t = self._create_tournament(res)
        self._add_tournament(new_t)
        return new_t

    async def destroy_tournament(self, t: Tournament):
        """ completely removes a tournament from Challonge

        |methcoro|

        Note:
            |from_api| Deletes a tournament along with all its associated records. There is no undo, so use with care!

        Raises:
            ChallongeException

        """
        found_t = find_local(self.tournaments, t.id)
        if found_t is None:
            print('Unreferenced tournament')
        else:
            self.tournaments.remove(found_t)
        await self.connection('DELETE', 'tournaments/{}'.format(t.id))


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
        ChallongeException

    """
    new_user = User(username, api_key, **kwargs)
    await new_user.validate()
    return new_user
