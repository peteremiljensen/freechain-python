import unittest
import datetime, json
from .. import block, loaf
from .miner import *

class TestBlockMethods(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        cls.l_1 = loaf.Loaf('test')
        cls.l_2 = loaf.Loaf('test', 'test', 'test')

        cls.b_1 = miner([cls.l_1], 0, '-1')
        cls.b_2 = miner([cls.l_2], 0, '-1')

        cls.b_3 = block.Block([cls.l_1], 0, "-1", "2012", 512, "test")

    def test_block_validate(self):
        self.assertTrue(self.b_1.validate())
        self.assertFalse(self.b_2.validate())
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
        b = block.Block.create_block_from_dict(dictio)
        self.assertTrue(b.validate())

if __name__ == '__main__':
    unittest.main()
