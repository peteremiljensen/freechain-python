import unittest
import threading
from ..node import *
from ..events import *
from ..common import *
#from .. import loaf
#from .. import block

class TestIntegration1(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        cls.connect_sema = threading.Semaphore(0)
        cls.e = Events.Instance()
        def connection_callback(websocket):
            cls.connect_sema.release()
        cls.e.register_callback(EVENTS_TYPE.CONNECTION_READY,
                                 connection_callback)

        cls.node_1 = Node(9000)
        cls.node_2 = Node(9001)
        cls.node_1.start()
        cls.node_2.start()

        cls.node_1.connect_node('localhost', 9001)
        cls.is_connected = cls.connect_sema.acquire(timeout=20)

    def test_connect_node(self):
        self.assertTrue(self.is_connected)

    def test_add_loaf(self):
        pass
        #loaf = Loaf("test123")
        #self.assertTrue(self.node_1.add_loaf(loaf))
        '''exists = False
        for l in self.node_1._loaf_pool:
            if l == loaf:
                exists = True
                break
        self.assertTrue(exists)'''
