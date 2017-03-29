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
    def __init__(self, loaves, height, previous_block_hash,
                 timestamp, nounce, hash=None):
        """ Block class constructor. If hash is not given, a new hash is created
        """
        self._block = {}
        self._block['loaves'] = loaves
        self._block['height'] = height
        self._block['previous_block_hash'] = previous_block_hash
        self._block['timestamp'] = timestamp
        self._block['nounce'] = nounce
        if hash == None:
            self._block['hash'] = hashlib.sha256(self.json()).hexdigest()
        else:
            self._block['hash'] = hash

    def json(self):
        """ Serializes block to a JSON formatted string, encodes to utf-8
            and returns
        """
        return json.dumps(self._block,
                          sort_keys=True,
                          cls=LoafEncoder).encode('utf-8')

    def get_height(self):
        """ Returns height of block """
        return self._block['height']

    def get_hash(self):
        """ Returns hash of block """
        return self._block['hash']

    def get_previous_block_hash(self):
        """ Returns hash of previous block """
        return self._block['previous_block_hash']

    def calculate_hash(self):
        """ Removes hash from block, calculates hash, reinserts old hash and
            returns new hash
        """
        hash_tmp = self._block['hash']
        del self._block['hash']
        hash_calc = hashlib.sha256(self.json()).hexdigest()
        self._block['hash'] = hash_tmp
        return hash_calc

    def validate(self):
        """ Validates block by validating all loaves in block and calling
            calculate_hash. returns true if hash is same as calculated hash
            and if the first 5 digit in the hash are all 0
        """
        for l in self._block['loaves']:
            if not l.validate():
                return False
        hash_calc = self.calculate_hash()
        return self._block['hash'] == hash_calc and \
            hash_calc[:4] == '0000'

    @staticmethod
    def create_block_from_dict(dictio):
        """ Creates block object from dictionary """
        loaves = []
        for loaf_raw in dictio['loaves']:
            loaves.append(Loaf.create_loaf_from_dict(loaf_raw))
        return Block(loaves, dictio['height'],
                     dictio['previous_block_hash'], dictio['timestamp'],
                     dictio['nounce'], dictio['hash'])

class BlockEncoder(LoafEncoder):
    def default(self, obj):
        if isinstance(obj, Block):
            return obj._block
        return LoafEncoder.default(self, obj)
