import hashlib
import datetime
import json

from blockchain.loaf import *

#  ______ _            _
#  | ___ \ |          | |
#  | |_/ / | ___   ___| | __
#  | ___ \ |/ _ \ / __| |/ /
#  | |_/ / | (_) | (__|   <
#  \____/|_|\___/ \___|_|\_\
#

class Block:
    def __init__(self, loafs, height, previous_block_hash,
                 timestamp, nounce, hash=None):
        self._block = {}
        self._block['loafs'] = loafs
        self._block['height'] = height
        self._block['previous_block_hash'] = previous_block_hash
        self._block['timestamp'] = timestamp
        self._block['nounce'] = nounce
        if hash == None:
            self._block['hash'] = hashlib.sha256(self.json()).hexdigest()
        else:
            self._block['hash'] = hash

    def json(self):
        return json.dumps(self._block,
                          sort_keys=True,
                          cls=LoafEncoder).encode('utf-8')

    def get_height(self):
        return self._block['height']

    def get_hash(self):
        return self._block['hash']

    def get_previous_block_hash(self):
        return self._block['previous_block_hash']

    def calculate_hash(self):
        hash_tmp = self._block['hash']
        del self._block['hash']
        hash_calc = hashlib.sha256(self.json()).hexdigest()
        self._block['hash'] = hash_tmp
        return hash_calc

    def validate(self):
        for l in self._block['loafs']:
            if not l.validate():
                return False
        hash_calc = self.calculate_hash()
        return self._block['hash'] == hash_calc and \
            hash_calc[:5] == '00000'

    @staticmethod
    def create_block_from_dict(dictio):
        return Block(dictio['loafs'], dictio['height'],
                     dictio['previous_block_hash'], dictio['timestamp'],
                     dictio['nounce'], dictio['hash'])

class BlockEncoder(LoafEncoder):
    def default(self, obj):
        if isinstance(obj, Block):
            return obj._block
        return LoafEncoder.default(self, obj)
