import sys
import threading

from blockchain.loaf import *
from blockchain.block import *

class Chain():
    def __init__(self):
        genesis_block = Block.create_block_from_json('{"hash": "000002eae755addb7693ac1a1740d36ecc3c843b21affde7271eeb5a0c8cb6cd", "loafs": [], "nounce": 2104806, "previous_block_hash": "-1", "timestamp": "2017-03-21 14:49:34.218393"}')
        self._chain = [genesis_block]
        self._chain_lock = threading.RLock()

    def add_block(self, block):
        with self._chain_lock:
            if block.validate() and \
               self._chain[-1].get_hash() == block.get_previous_block_hash():
                self._chain.append(block)
                return True
            else:
                return False

    def get_block(self, height):
        with self._chain_lock:
            return self._chain[height]

    def get_length(self):
        with self._chain_lock:
            return len(self._chain)

    def mine_block(self, loafs):
        timestamp = str(datetime.datetime.now())
        previous_block_hash = self._chain[-1].get_hash()
        nounce = 0
        block = None
        while True:
            block = Block(loafs, previous_block_hash, timestamp, nounce)
            if block.get_hash()[:5] == '00000':
                return block
            nounce += 1

    def json(self):
        return json.dumps(self._chain,
                          sort_keys=True,
                          cls=BlockEncoder).encode('utf-8')

