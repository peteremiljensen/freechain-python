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
            {'loaves': [], 'nounce': 82743408,
             'previous_block_hash': '-1', 'height': 0,
             'timestamp': '2017-03-29 11:46:29.096909',
             'hash': '00000002a51fcae0911249bcb257f87cf00410d6c98c08ba649ba48a029e6154'})
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

    def remove_block(self, height):
        with self._chain_lock:
            self._chain = self._chain[:height]

    def get_block(self, height):
        """ Locks the chain and returns the height of the chain
        """
        with self._chain_lock:
            return self._chain[height]

    def get_length(self):
        """ Locks the chain and returns the length of the chain
        """
        with self._chain_lock:
            return len(self._chain)

    def validate(self):
        with self._chain_lock:
            for i in range(len(self._chain)):
                if not self._chain[i].validate():
                    return False
                elif i > 0 and self._chain[i].get_previois_block_hash() != \
                     self._chain[i-1].get_hash():
                    return False
            return True

    def json(self):
        """ Serializes chain to a JSON formatted string, encodes to utf-8
            and returns
        """
        return json.dumps(self._chain,
                          sort_keys=True,
                          cls=BlockEncoder).encode('utf-8')

    @staticmethod
    def create_chain_from_list(list):
        blocks = []
        for block_raw in list:
            blocks.append(Block.create_block_from_dict(block_raw))
        chain = Chain()
        chain._chain = blocks
        return chain
