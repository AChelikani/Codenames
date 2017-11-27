from game_code import *
from codename_game import CodenameGame
from codename_player import PlayerRole
from config import global_config as config

class ActiveGameStore:

	def __init__(self):
		self.active_games = {} # Dict[GameCode, GameManager]
		self.player_games = {} # Dict[str(PlayerId), GameCode]

	def create_game(self, game_code = create_game_code()):
		code_len = config.getGameCodeLen()
		new_code = generate_unique_game_code(code_len, self.active_games)
		active_games[new_code] = GameManager(new_code)
		return new_code

	def create_game_code(self):
		code_len = config.getGameCodeLen()
		return generate_unique_game_code(code_len, self.active_games)

	def contains_game(self, game_code):
		return game_code in self.active_games

	def update_game(self, game_code, new_game):
		self.active_games[game_code] = new_game

	def remove_player(self, player_id, game_code):
		self.active_games[game_code].remove_player(player_id)
		self.player_games[player_id] = game_code

	def add_player(self, player_id, game_code):
		new_player = self.active_games[game_code].add_player(player_id)
		self.player_games[player_id] = game_code
		return new_player

	def get_game(self, game_code):
		return self.active_games[game_code]

	def get_game_bundle(self, game_code):
		return self.get_game(game_code).serialize_game()

	def get_full_game_bundle(self, game_code, role):
		game_manager = self.get_game(game_code)
		game_bundle = game_manager.serialize_game_with_players()
		game_bundle['boardSize'] = config.getNumCards()
		if role is PlayerRole.SPYMASTER:
			game_bundle['map'] = game_manager.game.map.serialize()
		return game_bundle