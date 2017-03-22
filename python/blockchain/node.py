import threading
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

        self._loop = asyncio.new_event_loop()
        self._server_thread = threading.Thread(target=self._start_server_thread,
                                               args=(self._loop,), daemon=True)

    def start(self):
        self._server_thread.start()

    def broadcast_loaf(self, loaf):
        print ("HEJ MED JER ALLE", loaf)

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

    async def _server(self, websocket, path):
        loop = asyncio.get_event_loop()
        loop.call_soon_threadsafe(self.broadcast_loaf, 2)
        name = await websocket.recv()
        print("< {}".format(name))

        greeting = "Hello {}!".format(name)
        await websocket.send(greeting)
        print("> {}".format(greeting))

    def _start_server_thread(self, loop):
        asyncio.set_event_loop(loop)
        start_server = websockets.serve(self._server, 'localhost', self._port)
        loop.run_until_complete(start_server)
        loop.run_forever()
