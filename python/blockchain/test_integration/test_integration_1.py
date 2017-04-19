import unittest
import threading
from ..node import *
from ..events import *
from ..common import *
from .. import loaf
from .. import block

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

        cls.loaf = Loaf("test123")
        cls.block = None

    def test_1_connect_node(self):
        self.assertTrue(self.is_connected)

    def test_2_add_loaf(self):
        self.assertTrue(self.node_1.add_loaf(self.loaf))
        exists = False
        for l in self.node_1._loaf_pool:
            if l == self.loaf.get_hash():
                exists = True
                break
        self.assertTrue(exists)

    def test_3_broadcast_loaf(self):
        self.node_1.broadcast_loaf(self.loaf)
        loaf_sema = threading.Semaphore(0)
        received_loaf = None
        def loaf_callback(loaf):
            loaf_sema.release()
            received_loaf = loaf
        self.e.register_callback(EVENTS_TYPE.RECEIVED_LOAF, loaf_callback)
        self.assertTrue(loaf_sema.acquire(timeout=20))

        exists = False
        for l in self.node_2._loaf_pool:
            if l == self.loaf.get_hash():
                exists = True
                break
        self.assertTrue(exists)

    def test_4_mining(self):
        self.block = self.node_1.mine()
        self.assertEqual(self.block.get_loaves()[0].get_hash(),
                         self.loaf.get_hash())
        self.assertTrue(self.block.validate())
