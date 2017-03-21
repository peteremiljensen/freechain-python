import asyncio
import websockets
import block
import loaf

class Node():
    def __init__(self, address, port):
        self._address = address
        self._port = port
        self._nodes = []

    def broadcast_loaf(loaf):
        pass

    def connect_node():
        # establish connection
        self.query_length()
        if local_length < queried_length:
            self.request_blocks()

    def query_length():
        pass
    def request_blocks():
        pass
    def received_block(block):
        # validate block
        # check if new
        # forward block
        pass
    def received_loaf(loaf):
        # validate loaf
        # check if new
        # forward loaf
        pass
