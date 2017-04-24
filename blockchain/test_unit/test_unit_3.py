import unittest
import json
from .. import chain, block, loaf
from .miner import *

class TestChainMethods(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        cls.chain = chain.Chain()
        cls.b_1 = mine([], cls.chain.get_block(0))
        cls.b_2 = block.Block([], 0, "-1", "2012", 512, "test")

    def test_add_block(self):
        self.assertTrue(self.chain.add_block(self.b_1))
        self.assertFalse(self.chain.add_block(self.b_2))

    def test_remove_blocks(self):
        height = self.chain.get_length()
        self.chain.remove_block(height-1)
        self.assertEqual(height-1, self.chain.get_length())

    def test_get_block(self):
        length = self.chain.get_length()
        prev_block = self.chain.get_block(length - 1)
        b = mine([], prev_block)
        self.chain.add_block(b)
        self.assertEqual(b, self.chain.get_block(self.chain.get_length()-1))

    def test_json(self):
        c = chain.Chain()
        genesis = json.loads(c.json().decode('utf-8'))[0]
        self.assertEqual(genesis, json.loads(c._chain[0].json().decode('utf-8')))

    def test_create_chain_from_list(self):
        chain_list = [json.loads(self.b_1.json().decode('utf-8'))]
        c = chain.Chain.create_chain_from_list(chain_list)
        self.assertEqual(c.get_block(0).get_hash(), self.b_1.get_hash())

if __name__ == '__main__':
    unittest.main()
