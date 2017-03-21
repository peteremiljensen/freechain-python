import hashlib
import datetime
import json
from blockchain.loaf import *

class Block:
    def __init__(self, loafs, previous_block_hash,
                 timestamp, nounce, hash=None):
        self._block = {}
        self._block['loafs'] = loafs
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

    def get_hash(self):
        return self._block['hash']

    def get_previous_block_hash():
        return self._block['previous_block_hash']

    def calculate_hash(self):
        hash_tmp = self._block['hash']
        del self._block['hash']
        hash_calc = hashlib.sha256(self.json()).hexdigest()
        self._block['hash'] = hash_tmp
        return hash_calc

    def validate(self):
        for l in self._block['loafs']:
            if l.validate() == False:
                return False
        hash_calc = self.calculate_hash()
        return self._block['hash'] == hash_calc and \
            hash_calc[:4] == '0000'

    @staticmethod
    def create_block_from_json(json_string):
        dump = json.loads(json_string)
        loafs = []
        for l in dump['loafs']:
            loafs.append(Loaf.create_loaf_from_json(json.dumps(l)))
        return Block(loafs, dump['previous_block_hash'], dump['timestamp'],
                     dump['nounce'], dump['hash'])
