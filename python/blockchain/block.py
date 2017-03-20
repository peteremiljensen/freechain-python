import hashlib
import datetime
import json

class Block:
	def __init__(self, loafs, previous_block):
		self._block = {}
		self._block['height'] = previous_block.height
		self._block['timestamp'] = str(datetime.datetime.now())
		self._block['loafs'] = loafs
		self._block['previous_block'] = previous_block
