import unittest
import threading
from ..node import *
from ..events import *
from ..common import *
from .. import loaf
from .. import block

block = None

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
        cls.node_3 = Node(9002)
        cls.node_1.start()
        cls.node_2.start()
        cls.node_3.start()

        cls.node_1.connect_node('localhost', 9001)
        cls.is_connected = cls.connect_sema.acquire(timeout=20)

        cls.loaf = Loaf("test123")

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

    def test_3_add_loaf_twice(self):
        self.assertFalse(self.node_1.add_loaf(self.loaf))
        times = 0
        for l in self.node_1._loaf_pool:
            if l == self.loaf.get_hash():
                times += 1
                break
        self.assertEqual(times, 1)

    def test_4_broadcast_loaf(self):
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

    def test_5_mining(self):
        global block
        block = self.node_1.mine()
        self.assertEqual(block.get_loaves()[0].get_hash(),
                         self.loaf.get_hash())
        self.assertTrue(block.validate())

    def test_6_add_block(self):
        global block
        self.assertTrue(self.node_1.add_block(block))
        new_block = self.node_1._chain.get_block(1)
        self.assertEqual(new_block.get_hash(), block.get_hash())

    def test_7_loaf_added_twice_mined(self):
        self.assertFalse(self.node_1.add_loaf(self.loaf))
        times = 0
        for l in self.node_1._loaf_pool:
            if l == self.loaf.get_hash():
                times += 1
                break
        self.assertEqual(times, 0)

    def test_8_broadcast_block(self):
        global block
        self.node_1.broadcast_block(block)
        block_sema = threading.Semaphore(0)
        received_block = None
        def block_callback(block):
            block_sema.release()
            received_block = block
        self.e.register_callback(EVENTS_TYPE.RECEIVED_BLOCK, block_callback)
        self.assertTrue(block_sema.acquire(timeout=20))

        new_block = self.node_2._chain.get_block(1)
        self.assertEqual(new_block.get_hash(), block.get_hash())

    def test_9_replacing_chain(self):
        connect_sema = threading.Semaphore(0)
        def connection_callback(websocket):
            connect_sema.release()
        self.e.register_callback(EVENTS_TYPE.CONNECTION_READY,
                                 connection_callback)

        self.node_3.connect_node('localhost', 9000)
        self.assertTrue(connect_sema.acquire(timeout=20))

        replaced_sema = threading.Semaphore(0)
        def replaced_callback(websocket):
            replaced_sema.release()
        self.e.register_callback(EVENTS_TYPE.REPLACED_CHAIN,
                                 replaced_callback)

        self.assertTrue(replaced_sema.acquire(timeout=20))

        for i in range(2):
            self.assertEqual(self.node_1._chain.get_block(i).get_hash(),
                             self.node_3._chain.get_block(i).get_hash())

if __name__ == '__main__':
    unittest.main()
