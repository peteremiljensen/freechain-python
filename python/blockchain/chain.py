import sys
import threading

from blockchain.loaf import *
from blockchain.block import *

#   _____ _           _
#  /  __ \ |         (_)
#  | /  \/ |__   __ _ _ _ __
#  | |   | '_ \ / _` | | '_ \
#  | \__/\ | | | (_| | | | | |
#   \____/_| |_|\__,_|_|_| |_|
#

class Chain():
    def __init__(self):
        """ Chain class constructor
        """
        genesis_block = Block.create_block_from_dict(
            {'loafs': [], 'nounce': 7868515,
             'previous_block_hash': '-1', 'height': 0,
             'timestamp': '2017-03-29 11:28:48.355664',
             'hash': '0000001f0dc797d2c8034ff1e7dde91b2881230e60397d24f36ddea7ea09b1cd'})
        self._chain = [genesis_block]
        self._chain_lock = threading.RLock()

    def add_block(self, block):
        """ Locks the chain, validates a block and compares previous hash of
        the block and the blockchain. If hashes are the same, the block is
        validated, and the length of the chain matches the height of the block,
        the block is appended to the chain and the function returns True
        """
        with self._chain_lock:
            if block.validate() and \
               self._chain[-1].get_hash() == block.get_previous_block_hash() \
               and len(self._chain) == block.get_height():
                self._chain.append(block)
                return True
            else:
                return False

    def get_block(self, height):
        """ Locks the chain and returns the height of the chain
        """
        with self._chain_lock:
            return self._chain[height]

    def get_length(self):
        """ Locks the chain and returns the height of the chain
        """
        with self._chain_lock:
            return len(self._chain)

    def mine_block(self, loafs):
        """ Creates a block from given loaves. Sets nounce to 0 and generates
            a hash. If the first 5 digits in the hash are 0, the block is
            returned. If not, nounce is incremented by one and a new hash is
            generated
        """
        height = self.get_length()
        previous_block_hash = self._chain[-1].get_hash()
        timestamp = str(datetime.datetime.now())
        nounce = 0
        block = None
        while True:
            block = Block(loafs, height, previous_block_hash, timestamp, nounce)
            if block.get_hash()[:5] == '00000':
                return block
            nounce += 1

    def json(self):
        """ Serializes chain to a JSON formatted string, encodes to utf-8
            and returns
        """
        return json.dumps(self._chain,
                          sort_keys=True,
                          cls=BlockEncoder).encode('utf-8')
