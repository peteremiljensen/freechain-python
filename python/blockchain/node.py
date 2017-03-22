import asyncio

from blockchain.chain import Chain
from blockchain.loaf import Loaf
from blockchain.block import Block

class Node():
    def __init__(self, port):
        self._port = port
        self._nodes = set()

        self._chain = Chain()
        self._loaf_pool = {}

    def start(self):
        self._thread.start()

    def broadcast_loaf(self, loaf):
        pass

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

