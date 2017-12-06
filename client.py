from config import global_config as config
from enum import Enum
from random import choice
from uuid import uuid4
from player import Player, PlayerRole, PlayerTeam

class Client(object):
    def __init__(self, client_id):
        self.id = client_id
        self.players = {}

    @classmethod
    def new_client(cls):
        return cls(str(uuid4()))

    def get_num_players(self):
        ''' Returns number of players. '''
        return len(self.players)

    def add_new_player(self, used_avatars, team=None, role=None):
        ''' Creates new player and adds it. '''
        new_player = Player.new_player(used_avatars, team, role)
        self.add_player(new_player)
        return new_player

    def add_player(self, player):
        ''' Adds new player to active players and tracks avatar'''
        self.players[player.id] = player
        return player

    def remove_player(self, player_id):
        ''' Removes player from client'''
        player = self.players.pop(player_id, None)
        return player

    def get_players(self):
        ''' Returns active player id to player mapping. '''
        return self.players

    def get_player(self, player_id):
        ''' Returns corresponding player from the game '''
        if player_id not in self.players:
            ValueError('Player does not exist for id %s' % player_id)
        return self.players[player_id]

    def has_player(self, player_id):
        ''' Returns True if player_id is in players '''
        return player_id in self.players

    def has_role(self, team, role):
        ''' Returns whether or not a player with the given role exists '''
        for player in self.players.values():
            if player.role is role and player.team is team:
                return True
        return False

    def has_spymaster(self):
        ''' Returns SPYMASTER if there exists a player with the role of
            spymaster.
        '''
        for player in self.players.values():
            if player.role is PlayerRole.SPYMASTER:
                return PlayerRole.SPYMASTER
        return PlayerRole.OPERATIVE

    def switch_player_team(self, player_id):
        ''' Switches player team (RED/BLUE). '''
        if player_id not in self.players:
            raise ValueError("player id %s not found in players" % player_id)
        player = self.players[player_id]
        player.team = PlayerTeam.BLUE if player.team == PlayerTeam.RED else PlayerTeam.RED
        return

    def get_cookie(self):
        return {
            'client_id': self.id,
            'players': [p.id for p in self.get_players().values()]
		}

    def switch_player_role(self, player_id):
        ''' Switches player role (OPERATIVE/SPYMASTER). '''
        player = self.players[player_id]
        player.role = PlayerRole.SPYMASTER if player.role == PlayerRole.OPERATIVE else PlayerRole.OPERATIVE

    def serialize_players(self):
        ''' Serializes players to JSON object. '''
        return {
            'players': [p.serialize() for p in self.get_players().values()]
        }

    def serialize_players_mapping(self):
        ''' Serializes playerid to player mapping to JSON object. '''
        return {
            'players_mapping': [{'playerId': pId, 'player': p.serialize()} for pId, p in self.players.items()]
        }
