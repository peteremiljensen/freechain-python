import sys, os.path
import ast
import threading

from .loaf import *
from .block import *

#   _____ _           _
#  /  __ \ |         (_)
#  | /  \/ |__   __ _ _ _ __
#  | |   | '_ \ / _` | | '_ \
#  | \__/\ | | | (_| | | | | |
#   \____/_| |_|\__,_|_|_| |_|
#

class Chain():
    def __init__(self, chain_raw=None):
        """ Chain class constructor
        """
        self._chain = []
        self._chain_lock = threading.RLock()

    def add_block(self, block):
        """ Locks the chain, validates a block and compares previous hash of
        the block and the blockchain. If hashes are the same, the block is
        validated, and the length of the chain matches the height of the block,
        the block is appended to the chain and the function returns True
        """
        with self._chain_lock:
            if block.get_height() == 0 and self._chain == []:
                self._chain.append(block)
                return True
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
            for i in range(self.get_length()):
                if not self.get_block(i).validate():
                    return False
                if i > 0 and self.get_block(i).get_previous_block_hash() != \
                     self.get_block(i-1).get_hash():
                    return False
            return True

    def json(self):
        """ Serializes chain to a JSON formatted string, encodes to utf-8
            and returns
        """
        return json.dumps(self._chain,
                          sort_keys=True,
                          cls=BlockEncoder,
                          separators=(',', ':')).encode('utf-8')

    @staticmethod
    def read_chain(path):
        with open(path, 'r') as f:
            chain_list = ast.literal_eval(ast.literal_eval(f.read()).decode('utf-8'))
            return Chain.create_chain_from_list(chain_list)

    @staticmethod
    def save_chain(path, chain):
        with open(path, 'w') as f:
            f.write(str(chain.json()))

    @staticmethod
    def create_chain_from_list(list):
        blocks = []
        for block_raw in list:
            blocks.append(Block.create_block_from_dict(block_raw))
        chain = Chain()
        chain._chain = blocks
        return chain
