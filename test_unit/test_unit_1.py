import unittest
import datetime, json
import loaf
from validator import Validator

def loaf_validator(loaf):
    hash_calc = loaf.calculate_hash()
    return loaf.get_hash() == hash_calc

def block_validator(block):
    hash_calc = block.calculate_hash()
    return block.get_hash() == hash_calc and \
           hash_calc[:4] == '0000'

class TestLoafMethods(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        Validator.Instance().attach_loaf_validator(loaf_validator)
        Validator.Instance().attach_block_validator(block_validator)

        cls.data = 'test'
        cls.timestamp = str(datetime.datetime.now())
        cls.l = loaf.Loaf(cls.data, cls.timestamp)

        cls.hashtest = '12525718923'
        cls.l_hash = loaf.Loaf(cls.data, cls.timestamp, cls.hashtest)

    def test_loaf_validate(self):
        self.assertTrue(self.l.validate())
        self.assertFalse(self.l_hash.validate())

    def test_loaf_json(self):
        dictio = json.loads(self.l.json().decode('utf-8'))
        self.assertEqual(self.data, dictio['data'])
        self.assertEqual(self.timestamp, dictio['timestamp'])

        dictio = json.loads(self.l_hash.json().decode('utf-8'))
        self.assertEqual(self.hashtest, self.l_hash.get_hash())

    def test_create_loaf_from_dict(self):
        dictio = {'data': {'string':'test'},
                  'hash': '1821942a611ef2a8e882e7c335ef4d9' +
                          '66a141038f620bbea09f642a4f99a321e',
                  'timestamp': '2017-04-28 14:45:36.583997'}
        l = loaf.Loaf.create_loaf_from_dict(dictio)
        self.assertTrue(l.validate())
        dictio['data'] = 'test1'
        l = loaf.Loaf.create_loaf_from_dict(dictio)
        self.assertFalse(l.validate())

if __name__ == '__main__':
    unittest.main()
