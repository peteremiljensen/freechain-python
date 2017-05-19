import hashlib
import datetime
import json

from .loaf import *
from .validator import Validator

#  ______ _            _
#  | ___ \ |          | |
#  | |_/ / | ___   ___| | __
#  | ___ \ |/ _ \ / __| |/ /
#  | |_/ / | (_) | (__|   <
#  \____/|_|\___/ \___|_|\_\
#

class Block:
    def __init__(self, loaves, height, previous_block_hash,
                 timestamp=None, data={}, hash=None):
        """ Block class constructor. If hash is not given, a new hash is created
        """
        self._block = {}
        self._block['loaves'] = loaves
        self._block['height'] = height
        self._block['previous_block_hash'] = previous_block_hash
        if timestamp == None:
            self._block['timestamp'] = str(datetime.datetime.now())
        else:
            self._block['timestamp'] = timestamp
        self._block['data'] = data
        if hash == None:
            self._block['hash'] = hashlib.sha256(self.json()).hexdigest()
        else:
            self._block['hash'] = hash

    def __getitem__(self, key):
        return self._block['data'][key]

    def json(self):
        """ Serializes block to a JSON formatted string, encodes to utf-8
            and returns
        """
        return json.dumps(self._block,
                          sort_keys=True,
                          cls=LoafEncoder,
                          separators=(',', ':')).encode('utf-8')

    def get_loaves(self):
        return self._block['loaves']

    def get_height(self):
        """ Returns height of block """
        return self._block['height']

    def get_hash(self):
        """ Returns hash of block """
        return self._block['hash']

    def get_previous_block_hash(self):
        """ Returns hash of previous block """
        return self._block['previous_block_hash']

    def get_data(self):
        return self._block['data']

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
        return Validator.Instance().validate_block(self)

    @staticmethod
    def create_block_from_dict(dictio):
        """ Creates block object from dictionary """
        loaves = []
        for loaf_raw in dictio['loaves']:
            loaves.append(Loaf.create_loaf_from_dict(loaf_raw))
        return Block(loaves, dictio['height'],
                     dictio['previous_block_hash'], dictio['timestamp'],
                     dictio['data'], dictio['hash'])

class BlockEncoder(LoafEncoder):
    def default(self, obj):
        if isinstance(obj, Block):
            return obj._block
        return LoafEncoder.default(self, obj)
