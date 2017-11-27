from codename_game import CodenameGame
from codename_player import Player, PlayerTeam, PlayerRole

class GameManager(object):
    def __init__(self, game_code):
        self.game_code = game_code
        self.game = CodenameGame()
        self.players = {}
        # Keep track of disconnected players in case they come back
        self.dangling_players = {}
        self.used_avatars = []

    def get_num_players(self):
        return len(self.players)

    def add_player(self, player):
        self.players[player.id] = player
        self.used_avatars.append(player.avatar)
        return player

    def add_new_player(self):
        new_player = Player(self.used_avatars)
        self.add_player(new_player)
        return new_player

    def remove_player(self, player_id):
        player = self.players.pop(player_id, None)
        self.used_avatars.remove(player.avatar)
        self.dangling_players[player_id] = player
        return player

    def get_players(self):
        return self.players

    def get_dangling_players(self):
        return self.dangling_players

    def restore_player(self, player_id):
        player = self.dangling_players.pop(player_id)
        return self.add_player(player)

    def switch_player_team(self, player_id):
        if player_id not in self.players:
            raise ValueError("player id %s not found in players" % player_id)
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
