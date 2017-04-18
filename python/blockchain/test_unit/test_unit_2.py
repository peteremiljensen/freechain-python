import unittest
import datetime, json
from .. import block, loaf
from .miner import *

class TestBlockMethods(unittest.TestCase):

    def setUp(self):
        self.l_1 = loaf.Loaf('test')
        self.l_2 = loaf.Loaf('test', 'test', 'test')

        self.b_1 = miner([self.l_1], 0, '-1')
        self.b_2 = miner([self.l_2], 0, '-1')

        self.b_3 = block.Block([self.l_1], 0, "-1", "2012", 512, "test")

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

if __name__ == '__main__':
    unittest.main()
