import unittest
import threading, time, asyncio
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
        cls.node_4 = Node(9003)
        cls.node_1.start()
        cls.node_2.start()
        cls.node_3.start()
        cls.node_4.start()
        time.sleep(1)

        cls.node_1.connect_node('localhost', 9001)
        cls.is_connected = cls.connect_sema.acquire(timeout=20)

        cls.loaf = Loaf("test123")

    def test_a_connect_node(self):
        self.assertTrue(self.is_connected)

    def test_b_add_loaf(self):
        self.assertTrue(self.node_1.add_loaf(self.loaf))
        exists = False
        for l in self.node_1._loaf_pool:
            if l == self.loaf.get_hash():
                exists = True
                break
        self.assertTrue(exists)
        self.assertFalse(self.node_1.add_loaf(Loaf("t", "t", "t")))

    def test_c_add_loaf_twice(self):
        self.assertFalse(self.node_1.add_loaf(self.loaf))
        times = 0
        for l in self.node_1._loaf_pool:
            if l == self.loaf.get_hash():
                times += 1
                break
        self.assertEqual(times, 1)

    def test_d_broadcast_loaf(self):
        self.node_1.broadcast_loaf(self.loaf)
        loaf_sema = threading.Semaphore(0)
        def loaf_callback(loaf):
            loaf_sema.release()
        self.e.register_callback(EVENTS_TYPE.RECEIVED_LOAF, loaf_callback)
        self.assertTrue(loaf_sema.acquire(timeout=20))
        self.assertTrue(self.loaf.get_hash() in
                        self.node_2._loaf_pool.keys())

    def test_e_mining(self):
        global block
        block = self.node_1.mine()
        self.assertEqual(block.get_loaves()[0].get_hash(),
                         self.loaf.get_hash())
        self.assertTrue(block.validate())

    def test_f_add_block(self):
        global block
        self.assertTrue(self.node_1.add_block(block))
        new_block = self.node_1._chain.get_block(1)
        self.assertEqual(new_block.get_hash(), block.get_hash())

    def test_g_loaf_added_twice_mined(self):
        self.assertFalse(self.node_1.add_loaf(self.loaf))
        times = 0
        for l in self.node_1._loaf_pool:
            if l == self.loaf.get_hash():
                times += 1
                break
        self.assertEqual(times, 0)

    def test_h_broadcast_block(self):
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

    def test_i_replacing_chain(self):
        self.node_3.connect_node('localhost', 9000)

        replaced_sema = threading.Semaphore(0)
        def replaced_callback(websocket):
            replaced_sema.release()
        self.e.register_callback(EVENTS_TYPE.BLOCKS_ADDED,
                                 replaced_callback)

        self.assertTrue(replaced_sema.acquire(timeout=20))

        for i in range(2):
            self.assertEqual(self.node_1._chain.get_block(i).get_hash(),
                             self.node_3._chain.get_block(i).get_hash())

    def test_j_longer_chain(self):
        block_1 = self.node_4.mine()
        self.assertTrue(self.node_4.add_block(block_1))
        block_2 = self.node_4.mine()
        self.assertTrue(self.node_4.add_block(block_2))
        block_3 = self.node_4.mine()
        self.assertTrue(self.node_4.add_block(block_3))
        block_4 = self.node_4.mine()
        self.assertTrue(self.node_4.add_block(block_4))

        self.node_1.add_loaf(self.loaf)
        block_5 = self.node_1.mine()
        self.assertTrue(self.node_1.add_block(block_5))

        self.assertTrue(self.loaf.get_hash() in
                        list(self.node_1._mined_loaves.keys()))

        self.node_1.connect_node('localhost', 9003)

        replaced_sema = threading.Semaphore(0)
        def replaced_callback(data):
            replaced_sema.release()
        self.e.register_callback(EVENTS_TYPE.BLOCKS_ADDED,
                                 replaced_callback)

        self.assertTrue(replaced_sema.acquire(timeout=20))

        for i in range(5):
            self.assertEqual(self.node_1._chain.get_block(i).get_hash(),
                             self.node_4._chain.get_block(i).get_hash())

        self.assertTrue(loaf.get_hash() in list(self.node_1._loaf_pool.keys()))
        self.assertTrue(loaf            in list(self.node_1._loaf_pool.values()))

    def test_k_unknown_type(self):
        response = self.node_1._json({'type': 'test'})
        self.node_1._network.broadcast(response)

        error_sema = threading.Semaphore(0)
        def error_callback(data):
            error_sema.release()
        self.e.register_callback(EVENTS_TYPE.RECEIVED_ERROR,
                                 error_callback)

        self.assertTrue(error_sema.acquire(timeout=20))

    def test_l_attribute_error(self):
        response = self.node_1._json({'type': 'response',
                                      'function': 'get_length'})
        self.node_1._network.broadcast(response)

        error_sema = threading.Semaphore(0)
        def error_callback(data):
            error_sema.release()
        self.e.register_callback(EVENTS_TYPE.RECEIVED_ERROR,
                                 error_callback)

        self.assertTrue(error_sema.acquire(timeout=20))

    def test_m_unsupported_function(self):
        response = self.node_1._json({'type': 'response',
                                      'function': 'test215'})
        self.node_1._network.broadcast(response)

        error_sema = threading.Semaphore(0)
        def error_callback(data):
            error_sema.release()
        self.e.register_callback(EVENTS_TYPE.RECEIVED_ERROR,
                                 error_callback)

        self.assertTrue(error_sema.acquire(timeout=20))

    def test_n_remove_block(self):
        pass

    def test_z_closed_connection(self):
        self.node_1._network.close_connections()

        closed_sema = threading.Semaphore(0)
        def closed_callback(data):
            closed_sema.release()
        self.e.register_callback(EVENTS_TYPE.CONNECTION_CLOSED,
                                 closed_callback)

        self.assertTrue(closed_sema.acquire(timeout=20))

if __name__ == '__main__':
    unittest.main()
