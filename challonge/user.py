from . import CHALLONGE_AUTO_GET_PARTICIPANTS, CHALLONGE_AUTO_GET_MATCHES
from .helpers import get_connection, find_local
from .tournament import Tournament, TournamentType


class User:
    """
    """
    def __init__(self, username, api_key, **kwargs):
        self.tournaments = None
        self.connection = get_connection(username, api_key, **kwargs)

    def _add_tournament(self, t: Tournament):
        if t is not None:
            if self.tournaments is None:
                self.tournaments = []
            self.tournaments.append(t)

    def _create_tournament(self, json_def):
        return Tournament(self.connection, json_def)

    async def validate(self):
        await self.connection('GET', 'tournaments')

    async def get_tournament(self, t_id: str, force_update=False) -> Tournament:
        found_t = find_local(self.tournaments, t_id)
        if force_update or found_t is None:
            res = await self.connection('GET', 'tournaments/{}'.format(t_id))
            found_t = self._create_tournament(res)
            self._add_tournament(found_t)
        return found_t

    async def get_tournaments(self, force_update=False) -> list:
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

    async def create_tournament(self, name: str, url: str, tournament_type=TournamentType.single_elimination, **params):
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
        found_t = find_local(self.tournaments, t.id)
        if found_t is None:
            print('Unreferenced tournament')
        else:
            self.tournaments.remove(found_t)
        await self.connection('DELETE', 'tournaments/{}'.format(t.id))


async def get_user(username, api_key, **kwargs):
    """ Creates a new user, validate its credentials and returns it
    Can raise
    """
    new_user = User(username, api_key, **kwargs)
    await new_user.validate()
    return new_user
