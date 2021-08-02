# flake8: noqa

__version__ = "1.9.0"
__author__ = "fp12"

AUTO_GET_PARTICIPANTS = True
AUTO_GET_MATCHES = True
USE_FIELDS_DESCRIPTORS = True
USE_EXCEPTIONS = True


from .helpers import APIException
from .user import User, get_user
from .tournament import Tournament
from .participant import Participant
from .match import Match
from .attachment import Attachment
from .enums import TournamentState, TournamentType, TournamentStateResult, DoubleEliminationEnding, RankingOrder, Pairing, MatchState
