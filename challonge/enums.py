from enum import Enum


class TournamentState(Enum):
    """ State a tournament can be in """
    pending = 'pending'
    open_ = 'open'  #: can't use `open`
    complete = 'complete'
    in_progress = 'in progress'


class TournamentType(Enum):
    """ Type of a tournament """
    single_elimination = 'single elimination'
    double_elimination = 'double elimination'
    round_robin = 'round robin'
    swiss = 'swiss'


class TournamentStateResult(Enum):
    """ State given from the Challonge API.
    Can be different from :class:`TournamentState`
    """
    underway = 0
    pending = 1


class DoubleEliminationEnding(Enum):
    """ Type of ending for double elimination tournaments """
    default = None  #: give the winners bracket finalist two chances to beat the losers bracket finalist
    single_match = 'single_match'  #: create only one grand finals match
    no_grand_finals = 'skip'  #: don't create a finals match between winners and losers bracket finalists


class RankingOrder(Enum):
    """ Order the ranking should be built upon """
    match_wins = 'match wins'
    game_wins = 'game wins'
    points_scored = 'points scored'
    points_difference = 'points difference'
    custom = 'custom'


class Pairing(Enum):
    """ Method of participant pairing when building matches """
    seeds = 0
    sequential = 1


class MatchState(Enum):
    """ State a match can be in """
    all_ = 'all'  #: can't use `all`
    open_ = 'open'  #: can't use `open`
    pending = 'pending'
    complete = 'complete'
