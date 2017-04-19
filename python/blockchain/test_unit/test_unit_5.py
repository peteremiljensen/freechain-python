import unittest
from .. import singleton

@Singleton
class SingletonTest:
    def __init__(self):
        pass

class TestSingletonMethods(unittest.TestCase):

    def setUp(self):
        pass
