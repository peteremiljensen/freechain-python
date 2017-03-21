import threading
import asyncio
import websockets
import time

from blockchain.chain import Chain
from blockchain.loaf import Loaf
from blockchain.block import Block

class Node():
    def __init__(self, port):
        self._port = port
        self._nodes = []

        self._chain = Chain()
        self._loaf_pool = {}

        loop = asyncio.get_event_loop()
        self._thread = threading.Thread(target=self._runner,
                                        args=(loop,),
                                        daemon=True)

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

    async def _handler(self, websocket, path):
        name = await websocket.recv()
        print("< {}".format(name))

        greeting = "Hello {}!".format(name)
        await websocket.send(greeting)
        print("> {}".format(greeting))

    def _runner(self, event_loop):
        asyncio.set_event_loop(event_loop)
        start_server = websockets.serve(self._handler, '0.0.0.0', self._port)
        asyncio.get_event_loop().run_until_complete(start_server)
        asyncio.get_event_loop().run_forever()
