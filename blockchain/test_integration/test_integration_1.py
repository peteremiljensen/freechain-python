import unittest
import threading, time, asyncio
from ..node import *
from ..events import *
from ..common import *
from .. import loaf
from .. import block

block = None

def loaf_validator(loaf):
    hash_calc = loaf.calculate_hash()
    return loaf.get_hash() == hash_calc

def block_validator(block):
    hash_calc = block.calculate_hash()
    return block.get_hash() == hash_calc and \
           hash_calc[:4] == '0000'

def attach(node):
    node.attach_loaf_validator(loaf_validator)
    node.attach_block_validator(block_validator)
    node.attach_consensus_check(consensus_check)
    node.attach_consensus(consensus)

def mine(loaves, prev_block):
    height = prev_block.get_height() + 1
    previous_block_hash = prev_block.get_hash()
    timestamp = str(datetime.datetime.now())
    nounce = 0
    block = None
    while True:
        block = Block(loaves, height, previous_block_hash, timestamp, nounce)
        if block.get_hash()[:4] == '0000':
            return block
        nounce += 1

    if block.validate():
        return block
    else:
        print(fail('block could not be mined'))
        return None

def consensus_check(local_length, rec_length):
    if local_length < rec_length:
        return True
    else:
        return False

def consensus(chain1, chain2):
    if chain1.get_length() < chain2.get_length():
        return chain2
    else:
        return chain1
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
        attach(cls.node_1)
        attach(cls.node_2)
        attach(cls.node_3)
        attach(cls.node_4)

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
        pool_keys = list(self.node_1._loaf_pool.keys())
        self.assertEqual(pool_keys.count(self.loaf.get_hash()), 1)

    def test_d_broadcast_loaf(self):
        self.node_1.broadcast_loaf(self.loaf)
        loaf_sema = threading.Semaphore(0)
        def loaf_callback(loaf):
            loaf_sema.release()
        self.e.register_callback(EVENTS_TYPE.RECEIVED_LOAF, loaf_callback)
        self.assertTrue(loaf_sema.acquire(timeout=20))
        self.assertTrue(self.loaf.get_hash() in self.node_2._loaf_pool.keys())

    def test_e_mining(self):
        global block
        loaves = self.node_1.get_loaves()
        chain_length = self.node_1._chain.get_length()
        prev_block = self.node_1._chain.get_block(chain_length-1)
        block = mine(loaves, prev_block)
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
        self.assertFalse(self.loaf.get_hash() in self.node_1._loaf_pool.keys())

    def test_h_broadcast_block(self):
        Loaf("test").validate()
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
        loaves = self.node_4.get_loaves()
        chain_length = self.node_4._chain.get_length()
        prev_block = self.node_4._chain.get_block(chain_length-1)
        block_1 = mine(loaves, prev_block)
        self.assertTrue(self.node_4.add_block(block_1))
        loaves = self.node_4.get_loaves()
        chain_length = self.node_4._chain.get_length()
        prev_block = self.node_4._chain.get_block(chain_length-1)
        block_2 = mine(loaves, prev_block)
        self.assertTrue(self.node_4.add_block(block_2))
        loaves = self.node_4.get_loaves()
        chain_length = self.node_4._chain.get_length()
        prev_block = self.node_4._chain.get_block(chain_length-1)
        block_3 = mine(loaves, prev_block)
        self.assertTrue(self.node_4.add_block(block_3))
        loaves = self.node_4.get_loaves()
        chain_length = self.node_4._chain.get_length()
        prev_block = self.node_4._chain.get_block(chain_length-1)
        block_4 = mine(loaves, prev_block)
        self.assertTrue(self.node_4.add_block(block_4))

        loaf2 = Loaf("test1")

        self.assertTrue(self.node_1.add_loaf(loaf2))
        loaves = self.node_1.get_loaves()
        chain_length = self.node_1._chain.get_length()
        prev_block = self.node_1._chain.get_block(chain_length-1)
        block_5 = mine(loaves, prev_block)
        self.assertTrue(self.node_1.add_block(block_5))

        self.assertTrue(loaf2.get_hash() in self.node_1._mined_loaves.keys())

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

        self.assertTrue(loaf2.get_hash() in list(self.node_1._loaf_pool.keys()))
        self.assertTrue(loaf2            in list(self.node_1._loaf_pool.values()))
        self.assertTrue(loaf2.get_hash() not in self.node_1._mined_loaves.keys())

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

    def test_n_save_read_chain(self):
        Chain.save_chain('test.bc', self.node_1._chain)
        chain = Chain.read_chain('test.bc')
        self.assertTrue(self.node_1._chain.validate())
        self.assertTrue(chain.validate())

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
