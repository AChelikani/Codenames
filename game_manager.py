from codename_game import CodenameGame
from codename_player import Player
from config import global_config as config
from random import choice

class GameManager(object):
    def __init__(self, game_code):
        self.game_code = game_code
        self.game = CodenameGame()
        self.players = {}
        self.available_avatars = config.getAvatars()

    def get_num_players(self):
        return len(self.players)

    def add_player(self, player_id):
        # choose a random avatar and remove it from available avatars
        # TODO?: this logic could be done on the fly saving precious memory
        #        if need-be
        avatar = choice(self.available_avatars)
        index = self.available_avatars.index(avatar)
        del self.available_avatars[index]

        new_player = Player(player_id, avatar)
        self.players[player_id] = new_player
        return new_player

    def remove_player(self, player_id):
        player = self.players.pop(player_id, None)
        self.available_avatars.append(player.avatar)
        return player

    def get_players(self):
        return self.players

    def get_game(self):
        return self.game
