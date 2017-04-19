import unittest
from .. import singleton

@singleton.Singleton
class SingletonTest:
    def __init__(self):
        pass

class TestSingletonMethods(unittest.TestCase):

    def test_call_error(self):
        with self.assertRaises(TypeError):
            test = SingletonTest()

    def test_instance_check(self):
        self.assertFalse(isinstance(SingletonTest.Instance(), unittest.TestCase))
        self.assertTrue(isinstance(SingletonTest.Instance(), SingletonTest))
