from enum import Enum
from random import choice

class PlayerTeam(Enum):
    BLUE = 'BLUE'
    RED = 'RED'

class PlayerRole(Enum):
    SPYMASTER = 'SPYMASTER'
    PLAYER = 'PLAYER'

class Player(object):
    def __init__(self, id, avatar):
        self.id = id
        self.avatar = avatar
        self.team = choice(list(PlayerTeam))
        self.role = choice(list(PlayerRole))

    # TODO: this should be swapped out with whatever serialization we choose
    def serialize(self):
        return {
        'id': self.id,
        'avatar': self.avatar,
        'team': self.team.value,
        'role': self.role.value
    }
