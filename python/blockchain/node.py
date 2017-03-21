import asyncio
import websockets
import block
import loaf

class Node():
    def __init__(self):
        self._blockchain = []
        self._loafs = []
        self._nodes = []
        return True

    def add_block(block):
        self._blockchain.append(block)
    def broadcast_loaf(loaf):
        self._loafs.append(loaf)

    def attach_block_validator():
        pass
    def attach_loaf_validator():
        pass
    def attach_consensus():
        pass

    def connect_node():
        # establish connection
        self.query_length()
        if local_length < queried_length:
            self.request_blocks()
        pass
    def query_length():
        pass
    def request_blocks():
        pass
    def received_block(block):
        # validate block
        # check if new
        self.add_block(block)
        # forward block
        pass
    def received_loaf(loaf):
        # validate loaf
        # check if new
        self.add_loaf(loaf)
        # forward loaf
        pass
