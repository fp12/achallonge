from enum import Enum


class MatchState(Enum):
    all_ = 'all'  # can't use `all`
    open_ = 'open'  # can't use `open`
    pending = 'pending'
    complete = 'complete'
