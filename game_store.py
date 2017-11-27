from game_code import *
from codename_game import CodenameGame
from game_manager import GameManager
from codename_player import PlayerRole
from config import global_config as config

class ActiveGameStore:

	def __init__(self):
		self.active_games = {} # Dict[GameCode, GameManager]
		# TODO: with session this might be deprecated
		self.player_games = {} # Dict[str(PlayerId), GameCode]

	def create_game(self, game_code_option = None):
		game_code = self.create_game_code() if game_code_option is None else game_code_option
		self.update_game(game_code, GameManager(game_code))
		return game_code

	def create_game_code(self):
		code_len = config.getGameCodeLen()
		return generate_unique_game_code(code_len, self.active_games)

	def contains_game(self, game_code):
		return game_code in self.active_games

	def contains_player(self, player_id):
		return player_id in self.player_games

	def update_game(self, game_code, new_game):
		self.active_games[game_code] = new_game

	def remove_player(self, player_id, game_code):
		game_manager = self.get_game(game_code)
		player = game_manager.remove_player(player_id)
		del self.player_games[player_id]
		return player

	def add_player(self, game_code):
		if game_code not in self.active_games:
			raise ValueError("%s not found in game store" % str(game_code))
		new_player = self.active_games[game_code].add_new_player()
		self.player_games[new_player.id] = game_code
		return new_player

	def get_game(self, game_code):
		if game_code not in self.active_games:
			raise ValueError("%s not found in game store" % str(game_code))
		return self.active_games[game_code]

	def get_game_code(self, player_id):
		if player_id not in self.player_games:
			raise ValueError("%s not found in game store" % player_id)
		return self.player_games[player_id]

	def get_game_bundle(self, game_code):
		return self.get_game(game_code).serialize_game()

	def get_full_game_bundle(self, game_code, role):
		game_manager = self.get_game(game_code)
		game_bundle = game_manager.serialize_game_with_players()
		game_bundle['boardSize'] = config.getNumCards()
		if role is PlayerRole.SPYMASTER:
			game_bundle['map'] = game_manager.game.map.serialize()
		return game_bundle

	def get_all_active_games(self):
		return [game_code.serialize() for game_code in self.active_games.keys()]

	def does_player_exist(self, game_code, player_id):
		game_manager = self.get_game(game_code)
		return player_id in game_manager.get_players()

	def is_player_dangling(self, game_code, player_id):
		game_manager = self.get_game(game_code)
		return player_id in game_manager.get_dangling_players()

	def restore_player(self, game_code, player_id):
		game_manager = self.get_game(game_code)
		assert(player_id in game_manager.get_dangling_players())
		self.player_games[player_id] = game_code
		return game_manager.restore_player(player_id)

	def get_lobby_bundle(self, game_code):
		game_manager = self.get_game(game_code)
		players = [p.serialize() for p in game_manager.get_players().values()]
		return {
			'players': players
		}
