from enum import Enum


class TournamentState(Enum):
    pending = 'pending'
    open_ = 'open'  # # can't use `open`
    complete = 'complete'
    in_progress = 'in progress'


class TournamentType(Enum):
    single_elimination = 'single elimination'
    double_elimination = 'double elimination'
    round_robin = 'round robin'
    swiss = 'swiss'


class TournamentStateResult(Enum):
    underway = 0
    pending = 1


class DoubleEliminationEnding(Enum):
    default = None
    single_match = 'single_match'
    no_grand_finals = 'skip'


class RankingOrder(Enum):
    match_wins = 'match wins'
    game_wins = 'game wins'
    points_scored = 'points scored'
    points_difference = 'points difference'
    custom = 'custom'


class Pairing(Enum):
    seeds = 0
    sequential = 1


class MatchState(Enum):
    all_ = 'all'  # can't use `all`
    open_ = 'open'  # can't use `open`
    pending = 'pending'
    complete = 'complete'
