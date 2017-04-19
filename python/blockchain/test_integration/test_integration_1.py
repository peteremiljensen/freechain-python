import unittest
import threading
from ..node import *
from ..events import *
from ..common import *

class TestIntegration1(unittest.TestCase):

    def setUp(self):
        self.connect_sema = threading.Semaphore(0)
        self.e = Events.Instance()
        def connection_callback(websocket):
            self.connect_sema.release()
        self.e.register_callback(EVENTS_TYPE.CONNECTION_READY,
                                 connection_callback)

        self.node_1 = Node(9000)
        self.node_2 = Node(9001)
        self.node_1.start()
        self.node_2.start()

        self.node_1.connect_node('localhost', 9001)
        self.is_connected = self.connect_sema.acquire(timeout=20)

    def test_connect_node(self):
        self.assertTrue(self.is_connected)
