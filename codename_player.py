from config import global_config as config
from enum import Enum
from random import choice
from uuid import uuid4

class PlayerTeam(Enum):
    BLUE = 'BLUE'
    RED = 'RED'

class PlayerRole(Enum):
    SPYMASTER = 'SPYMASTER'
    PLAYER = 'PLAYER'

class Player(object):
    def __init__(self, used_avatars):
        self.id = id
        self.team = choice(list(PlayerTeam))
        self.role = choice(list(PlayerRole))
        self.avatar = Player._get_avatar(used_avatars)
        self.id = str(uuid4())

    @staticmethod
    def _get_avatar(used_avatars):
        avatars = config.getAvatars()
        available_avatars = [x for x in avatars if x not in used_avatars]
        if len(available_avatars) < 1:
            raise ValueError('Out of avatars')
        avatar = choice(available_avatars)
        return avatar

    # TODO: this should be swapped out with whatever serialization we choose
    def serialize(self):
        return {
        'id': self.id, # this is technically bad practice but ¯\_(ツ)_/¯
        'avatar': self.avatar,
        'team': self.team.value,
        'role': self.role.value
    }
