import threading
import asyncio
import websockets
import queue

from blockchain.chain import Chain
from blockchain.loaf import Loaf
from blockchain.block import Block

class Node():
    def __init__(self, port):
        self._port = port
        self._server_nodes = set()
        self._client_nodes = set()
        self._queues = {}

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
        self._server_nodes.add(websocket)
        recv_queue = queue.Queue()
        send_queue = queue.Queue()
        self._queues[websocket] = (recv_queue, send_queue)
        try:
            while True:
                futures = []
                send_task = None
                try:
                    send_data = send_queue.get_nowait()
                    send_task = asyncio.ensure_future(websocket.send(send_data))
                    futures.append(send_task)
                except queue.Empty:
                    pass

                recv_task = asyncio.ensure_future(websocket.recv())
                futures.append(recv_task)
                done, pending = await asyncio.wait(
                    futures,
                    return_when=asyncio.FIRST_COMPLETED)

                if recv_task in done:
                    recv_data = recv_task.result()
                    recv_queue.put(recv_data)
                    print("Recieved data")
                else:
                    recv_task.cancel()
        finally:
            print ("Unregister")
            self._server_nodes.remove(websocket)
            del self._queues[websocket]

    def _start_server_thread(self, loop):
        asyncio.set_event_loop(loop)
        start_server = websockets.serve(self._server, 'localhost', self._port)
        loop.run_until_complete(start_server)
        loop.run_forever()
