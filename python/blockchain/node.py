from threading import Thread
import asyncio
import websockets

from blockchain.chain import Chain
from blockchain.loaf import Loaf
from blockchain.block import Block

class Node():
    def __init__(self, port):
        self._port = port
        self._nodes = set()

        self._chain = Chain()
        self._loaf_pool = {}

        loop = asyncio.new_event_loop()
        self._server_thread = Thread(target=self._start_server_thread,
                                     args=(loop,), daemon=True)

    def start(self):
        self._server_thread.start()

    def broadcast_loaf(self, loaf):
        print ("HEJ MED JER ALLE")

    def connect_node(self):
        # establish connection
        self.query_length()
        if local_length < queried_length:
            self.request_blocks()

    def query_length(self):
        pass
    def request_blocks(self):
        pass
    def received_block(self, block):
        # validate block
        # check if new
        # forward block
        pass
    def received_loaf(self, loaf):
        # validate loaf
        # check if new
        # forward loaf
        pass

    def _start_server_thread(self, loop):
        asyncio.set_event_loop(loop)
        pass
