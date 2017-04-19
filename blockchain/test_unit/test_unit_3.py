import unittest
import json
from .. import chain, block
from .miner import *

class TestChainMethods(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        cls.chain = chain.Chain()
        cls.b_1 = cls.chain.mine_block([])
        cls.b_2 = block.Block([], 0, "-1", "2012", 512, "test")

    def test_add_block(self):
        self.assertTrue(self.chain.add_block(self.b_1))
        self.assertFalse(self.chain.add_block(self.b_2))

    def test_remove_blocks(self):
        height = self.chain.get_length()
        self.chain.remove_blocks(height-1)
        self.assertEqual(height-1, self.chain.get_length())

    def test_get_block(self):
        b = self.chain.mine_block([])
        self.chain.add_block(b)
        self.assertEqual(b, self.chain.get_block(self.chain.get_length()-1))

    def test_json(self):
        c = chain.Chain()
        genesis = json.loads(c.json().decode('utf-8'))[0]
        self.assertEqual(genesis, json.loads(c._chain[0].json().decode('utf-8')))

if __name__ == '__main__':
    unittest.main()
