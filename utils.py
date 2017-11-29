from copy import deepcopy
class JSONUtils:

	@staticmethod
	def merge(a, b):
		''' Merges two JSON objects without conflict-resolution.
			If key-conflict exists, error is thrown.
		'''
		new_json = deepcopy(a)
		return JSONUtils.mix_in_place(new_json, b)

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
		if (new_child_key not in parent):
			raise ValueError("New child key conflicts with existing key in parent JSON object. Objects cannot be composed. ")
		parent[new_child_key] = new_child
		return parent