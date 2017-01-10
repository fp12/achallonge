# flake8: noqa

__version__ = "0.5.0"
__author__ = "fp12"

CHALLONGE_AUTO_GET_PARTICIPANTS = True
CHALLONGE_AUTO_GET_MATCHES = True
CHALLONGE_USE_FIELDS_DESCRIPTORS = True


from .helpers import ChallongeException
from .user import User, get_user
from .tournament import Tournament, TournamentType, DoubleEliminationEnding, RankingOrder, Pairing
from .participant import Participant
from .match import Match
from .attachment import Attachment
