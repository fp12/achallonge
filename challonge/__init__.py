__version__ = "0.5.0"
__author__ = "fp12"

CHALLONGE_AUTO_GET_PARTICIPANTS = True
CHALLONGE_AUTO_GET_MATCHES = True
CHALLONGE_USE_FIELDS_DESCRIPTORS = True


from .helpers import ChallongeException
from .user import User, get_user
