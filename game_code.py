from string import ascii_lowercase, digits
from random import SystemRandom

class GameCode:
	'''	Wrapper class around unique string id for generated games.
		Used to enforce key-type on accessing game store.
	'''

	def __init__(self, code):
		self.code = code

	def __hash__(self):
		''' Required for using GameCode as a key in any hashed structure. '''
		return self.code.__hash__()

	def __str__(self):
		return str(self.code)

	def __eq__(self, other):
		if isinstance(self, other.__class__):
			return self.code == other.code
		return False

	def __ne__(self, other):
		return not self.__eq__(other)   	

	def serialize(self):
		return self.__str__()

def generate_game_code(length):
	''' Generate a random game code of length `len` comprised of lowercase letters
		and numbers.
	'''
	return GameCode(''.join(SystemRandom().choice(ascii_lowercase + digits) for _ in range(length)))

def generate_unique_game_code(len, existing_codes):
	''' Given a set of existing codes, generate a unique code using
		`generate_game_code`. 
	'''
	game_code = generate_game_code(len)
	while game_code in existing_codes:
		game_code = generate_game_code(len)
	return game_code
