from game_code import *
from game_manager import GameManager
from codename_player import PlayerRole
from config import global_config as config
from utils import JSONUtils


class ActiveGameStore:
	''' In-memory store for games currently in play (active). '''

	def __init__(self):
		# Mapping of active game codes to game managers.
		self.active_games = {} # Dict[GameCode, GameManager]
		# TODO: with session this might be deprecated
		self.player_games = {} # Dict[str(PlayerId), GameCode]

	def create_game(self, game_code_option = None):
		''' Wrapper method for creating new game, and adding to game_store.
			If no game code is provided, a new game code is generated (and used).
		'''
		game_code = self.create_game_code() if game_code_option is None else game_code_option
		self.update_game(game_code, GameManager(game_code))
		return game_code

	def create_game_code(self):
		''' Wrapper method for generating new game code
			with the globally configured game code length.
		'''
		code_len = config.getGameCodeLen()
		return generate_unique_game_code(code_len, self.active_games)

	def remove_game(self, game_code):
		if game_code not in self.active_games:
			raise ValueError("%s not found in game store" % str(game_code))
		del self.active_games[game_code]

	def contains_game(self, game_code):
		''' Checks if active game store contains given game code. '''
		return game_code in self.active_games

	def contains_player(self, player_id):
		''' Checks if active game store contains given player id. '''
		return player_id in self.player_games

	def update_game(self, game_code, new_game):
		''' Overrides stored game at given game code with new provided game. '''
		self.active_games[game_code] = new_game

	def remove_player(self, player_id, game_code):
		''' Removes player from corresponding game manager AND player id to game mapping. '''
		game_manager = self.get_game(game_code)
		player = game_manager.remove_player(player_id)
		del self.player_games[player_id]
		return player

	def add_player(self, game_code):
		''' Adds player to specified game, AND updates player id to game mapping. '''
		if game_code not in self.active_games:
			raise ValueError("%s not found in game store" % str(game_code))
		new_player = self.active_games[game_code].add_new_player()
		self.player_games[new_player.id] = game_code
		return new_player

	def get_game(self, game_code):
		''' Returns specified game by game code.'''
		if game_code not in self.active_games:
			raise ValueError("%s not found in game store" % str(game_code))
		return self.active_games[game_code]

	def get_game_code(self, player_id):
		''' Returns specified game code by player id. '''
		if player_id not in self.player_games:
			raise ValueError("%s not found in game store" % player_id)
		return self.player_games[player_id]

	def get_game_bundle(self, game_code):
		'''	Returns JSON bundle of all dynamic game information
			that changes incrementally on each turn (for the specified game).
			This includes:
				- GameManager
					- Game code
					- Codename game
						- Deck
						- Red count
						- Blue count
						- Current turn
						- Current clue
						- Activity log
		'''
		return self.get_game(game_code).serialize_game()

	def get_full_game_bundle(self, game_code, role):
		'''	Returns JSON bundle of all game information (for the specified game).
			This includes:
				- GameManager
					- Game code
					- List of serialized playerid to player mapping
					- Board size
					- Map card (iff (if-only-if) SPYMASTER)
					- Codename game
						- Deck
						- Red count
						- Blue count
						- Current turn
						- Current clue
						- Activity log
		'''
		game_manager = self.get_game(game_code)
		game_bundle = game_manager.serialize_game()
		JSONUtils.merge_in_place(game_bundle, game_manager.serialize_players_mapping())
		JSONUtils.include_in_place(game_bundle, 'boardSize', str(config.getNumCards()))
		if role is PlayerRole.SPYMASTER:
			JSONUtils.include_in_place(game_bundle, 'map', game_manager.game.map_card.serialize())
		return game_bundle

	def get_all_active_games(self):
		''' Returns in-memory list of all active game codes. '''
		return [game_code.serialize() for game_code in self.active_games.keys()]

	def does_player_exist(self, game_code, player_id):
		''' Checks if specified player exists in specified game. '''
		game_manager = self.get_game(game_code)
		return player_id in game_manager.get_players()

	def is_player_dangling(self, game_code, player_id):
		''' Checks if player had previously disconnected from game. '''
		game_manager = self.get_game(game_code)
		return player_id in game_manager.get_dangling_players()

	def restore_player(self, game_code, player_id):
		''' Restores player to active player list in game. '''
		game_manager = self.get_game(game_code)
		assert(player_id in game_manager.get_dangling_players())
		self.player_games[player_id] = game_code
		return game_manager.restore_player(player_id)

	def get_lobby_bundle(self, game_code):
		''' Gets JSON "lobby bundle" of all active players in game. '''
		game_manager = self.get_game(game_code)
		return game_manager.serialize_players()

game_store = ActiveGameStore()
