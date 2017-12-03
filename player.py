from config import global_config as config
from enum import Enum
from random import choice
from uuid import uuid4

class PlayerTeam(Enum):
    BLUE = 'Blue'
    RED = 'Red'

class PlayerRole(Enum):
    SPYMASTER = 'Spymaster'
    OPERATIVE = 'Operative'


class Player(object):

	# TODO: Move sampling logic to Player static constructor,
	# 	and make constructor a value/direct field assignment constructor. (Done)
	# TODO: Document change
    def __init__(self, id, team, role, avatar):
    	self.id = id
    	self.team = team
    	self.role = role
    	self.avatar = avatar

    @classmethod
    def new_player(cls, used_avatars):
        return cls(id=str(uuid4()),
                   team=choice(list(PlayerTeam)),
                   role=choice(list(PlayerRole)),
                   avatar=Player._get_avatar(used_avatars))

    @staticmethod
    def _get_avatar(used_avatars, pref=None):
        if pref is not None and pref not in used_avatars:
            return pref
        avatars = config.getAvatars()
        available_avatars = [x for x in avatars if x not in used_avatars]
        if len(available_avatars) < 1:
            raise ValueError('Out of avatars')
        avatar = choice(available_avatars)
        return avatar

    # TODO: this should be swapped out with whatever serialization we choose
    def serialize(self):
        return {
        'id': self.id,
        'avatar': self.avatar,
        'team': self.team.value,
        'role': self.role.value
    }
