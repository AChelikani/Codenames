from string import ascii_lowercase, digits
from random import SystemRandom
from typing import NewType

class GameCode:

	def __init__(self, code):
		self.code = code

	def __hash__(self):
		return self.code.__hash__()

	def __str__(self):
		return str(self.code)

	def serialize(self):
		return self.__str__()

# Generate a random game code of length `len` comprised of lowercase letters
# and numbers
def generate_game_code(length):
    return GameCode(''.join(SystemRandom().choice(ascii_lowercase + digits) for _ in range(length)))

# Given a set of existing codes, generate a unique code using
# `generate_game_code`
def generate_unique_game_code(len, existing_codes):
    game_code = generate_game_code(len)
    while game_code in existing_codes:
        game_code = generate_game_code(len)
    return game_code
