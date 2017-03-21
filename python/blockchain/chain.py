from blockchain.loaf import *
from blockchain.block import *

class Chain():
    def __init__(self):
        genesis_block = Block.create_block_from_json('{"hash": "000002eae755addb7693ac1a1740d36ecc3c843b21affde7271eeb5a0c8cb6cd", "loafs": [], "nounce": 2104806, "previous_block_hash": "-1", "timestamp": "2017-03-21 14:49:34.218393"}')
        self._chain = [genesis_block]

    def add_block(self, block):
        return True
