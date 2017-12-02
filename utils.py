from copy import deepcopy
from constants import GAME_CODE_KEY, CLIENT_ID_KEY
from flask_socketio import emit
from functools import partial


class EmitEvent(object):
	def __init__(self, *args, **kwargs):
		self.args = args
		self.kwargs = kwargs
		self.emit_event = partial(emit, *args, **kwargs)

	def emit(self):
		self.emit_event()



class JSONUtils:

	@staticmethod
	def merge(a, b):
		''' Merges two JSON objects without conflict-resolution.
			If key-conflict exists, error is thrown.
		'''
		new_json = deepcopy(a)
		return JSONUtils.merge_in_place(new_json, b)

	@staticmethod
	def merge_in_place(a, b):
		''' Merges two JSON objects in-place (to `a`)without conflict-resolution.
			If key-conflict exists, error is thrown.
		'''
		for (key_b, val_b) in b.items():
			if key_b in a:
				raise ValueError("Conflicting (equivalent) keys found in JSON objects. Objects cannot be merged. ")
			a[key_b] = val_b
		return a

	@staticmethod
	def include(parent, new_child_key, new_child):
		''' Creates new JSON object with new field/value mapping added.
			Throws error on existing key conflict.
		'''
		new_json = deepcopy(parent)
		return JSONUtils.include_in_place(new_json, new_child_key, new_child)

	@staticmethod
	def include_in_place(parent, new_child_key, new_child):
		if (new_child_key in parent):
			raise ValueError("New child key conflicts with existing key in parent JSON object. Objects cannot be composed. ")
		parent[new_child_key] = new_child
		return parent


# Given a session return the game_code and player_id from it
def get_session_data(session):
    if GAME_CODE_KEY not in session:
        err_msg = 'Game session not found! Maybe it has ended or been deleted!'
        raise ValueError(err_msg)
    if CLIENT_ID_KEY not in session:
        err_msg = """It looks like your session ended unexpectedly, please
                     refresh the page."""
        raise ValueError(err_msg)
    game_code = session[GAME_CODE_KEY]
    client_id = session[CLIENT_ID_KEY]
    return game_code, client_id
