from codename_game import CodenameGame
from codename_player import Player, PlayerTeam, PlayerRole
from config import global_config as config
from random import choice

class GameManager(object):
    def __init__(self, game_code):
        self.game_code = game_code
        self.game = CodenameGame()
        self.players = {}
        self.used_avatars = []

    def get_num_players(self):
        return len(self.players)

    def add_player(self, player_id):
        avatars = config.getAvatars()
        available_avatars = [x for x in avatars if x not in self.used_avatars]
        avatar = choice(available_avatars)

        self.used_avatars.append(avatar)

        new_player = Player(player_id, avatar)
        self.players[player_id] = new_player
        return new_player

    def remove_player(self, player_id):
        player = self.players.pop(player_id, None)
        self.used_avatars.remove(player.avatar)
        return player

    def get_players(self):
        return self.players

    def switch_player_team(self, player_id):
        player = self.players[player_id]
        player.team = PlayerTeam.BLUE if player.team == PlayerTeam.RED else PlayerTeam.RED
        return

    def switch_player_role(self, player_id):
        player = self.players[player_id]
        player.role = PlayerRole.SPYMASTER if player.role == PlayerRole.PLAYER else PlayerRole.PLAYER

    def get_game(self):
        return self.game

    def serialize_game(self):
        game_bundle = self.game.serialize()
        game_bundle['gameCode'] = str(self.game_code)
        return game_bundle

    def serialize_game_with_players(self):
        game_bundle = self.serialize_game()
        game_bundle['players'] = [{'playerId': playerId, 'player': player.serialize()} for playerId, player in self.players.iteritems()]
        return game_bundle