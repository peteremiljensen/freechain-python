import unittest
import datetime, json
from .. import loaf

class TestLoafMethods(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
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
        dictio = {'data': 'test', 'hash': 'fa7fa7f32d318a962cbb8b52acb52' +
                  '60c3f5beee4ea5d882bab6459f2376a85fd',
                  'timestamp': '2017-04-18 14:58:01.696432'}
        l = loaf.Loaf.create_loaf_from_dict(dictio)
        self.assertTrue(l.validate())
        dictio['data'] = 'test1'
        l = loaf.Loaf.create_loaf_from_dict(dictio)
        self.assertFalse(l.validate())

if __name__ == '__main__':
    unittest.main()
