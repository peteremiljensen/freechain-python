import unittest
import datetime, json
from ..chain import *
from ..block import *
from ..loaf import *
from .miner import *
from ..validator import *

def loaf_validator(loaf):
    hash_calc = loaf.calculate_hash()
    return loaf.get_hash() == hash_calc

def block_validator(block):
    hash_calc = block.calculate_hash()
    return block.get_hash() == hash_calc and \
           hash_calc[:4] == '0000'

class TestBlockMethods(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        Validator.Instance().attach_loaf_validator(loaf_validator)
        Validator.Instance().attach_block_validator(block_validator)

        cls.chain = Chain()

        cls.l_1 = Loaf('test')
        cls.l_2 = Loaf('test', 'test', 'test')

        genesis_block = Block.create_block_from_dict(
            {"hash":"000077dbf86e9c0d593ac746a0658d88b966ddd0a132dcf9294c23a929ed4573",
             "height":0, "loaves":[], "data":{"nounce":27413},
             "previous_block_hash":"-1",
             "timestamp":"2017-05-01 15:16:52.579123"})

        cls.chain._chain = [genesis_block]
        cls.b_1 = mine([cls.l_1], cls.chain.get_block(0))
        #cls.b_2 = mine([cls.l_2], cls.chain()

        cls.b_3 = Block([cls.l_1], 0, "-1", "2012", 512, "test")

    def test_block_validate(self):
        self.assertTrue(self.b_1.validate())
        #self.assertFalse(self.b_2.validate())
        self.assertFalse(self.b_3.validate())

    def test_json(self):
        dictio = json.loads(self.b_3.json().decode('utf-8'))
        self.assertEqual(json.loads(self.l_1.json().decode('utf-8')),
                         dictio['loaves'][0])

    def test_get_methods(self):
        self.assertEqual(self.b_3.get_loaves(), [self.l_1])
        self.assertEqual(self.b_3.get_height(), 0)
        self.assertEqual(self.b_3.get_hash(), "test")
        self.assertEqual(self.b_3.get_previous_block_hash(), "-1")

    def test_create_block_from_dict(self):
        dictio = json.loads(self.b_1.json().decode('utf-8'))
        b = Block.create_block_from_dict(dictio)
        self.assertTrue(b.validate())

if __name__ == '__main__':
    unittest.main()
