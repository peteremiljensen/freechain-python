import unittest
import json
from ..chain import *
from ..block import *
from ..loaf import *
from .miner import *

class TestChainMethods(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        cls.chain = Chain()
        cls.b_1 = mine([], cls.chain.get_block(0))
        cls.b_2 = Block([], 0, "-1", "2012", 512, "test")

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
        c = Chain()
        genesis = json.loads(c.json().decode('utf-8'))[0]
        self.assertEqual(genesis, json.loads(c._chain[0].json().decode('utf-8')))

    def test_create_chain_from_list_and_validate(self):
        chain_list = [json.loads(self.b_1.json().decode('utf-8'))]
        c = Chain.create_chain_from_list(chain_list)
        self.assertEqual(c.get_block(0).get_hash(), self.b_1.get_hash())
        self.assertTrue(c.validate())
        chain_list.append(json.loads(self.b_2.json().decode('utf-8')))
        c = Chain.create_chain_from_list(chain_list)
        self.assertFalse(c.validate())

if __name__ == '__main__':
    unittest.main()
