import threading
import asyncio
import websockets
import queue
import time

from blockchain.chain import Chain
from blockchain.loaf import Loaf
from blockchain.block import Block

class Node():
    def __init__(self, port):
        self._port = port
        self._nodes = set()
        self._queues = {}

        self._chain = Chain()
        self._loaf_pool = {}

        self._server_thread = threading.Thread(target=self._start_server_thread,
                                               daemon=True)
        self._worker_thread = threading.Thread(target=self._worker_thread,
                                               daemon=True)

    def start(self):
        self._server_thread.start()
        self._worker_thread.start()

    def connect_node(self, ip):
        threading.Thread(target=self._start_client_thread,
                         args=(ip,), daemon=True).start()

    def broadcast(self, data):
        for queue in list(self._queues.values()):
            queue[1].put(data)

    async def _server(self, websocket, path):
        await self._protocol(websocket, True)

    async def _client(self, ip):
        async with websockets.connect('ws://' + ip + ':9000') as websocket:
            await self._protocol(websocket, False)

    async def _protocol(self, websocket, server):
        self._nodes.add(websocket)
        recv_queue = queue.Queue()
        send_queue = queue.Queue()
        self._queues[websocket] = (recv_queue, send_queue)
        try:
            while True:
                futures = []
                send_task = None
                recv_task = asyncio.ensure_future(websocket.recv())
                futures.append(recv_task)
                try:
                    data = send_queue.get_nowait()
                    send_task = asyncio.ensure_future(websocket.send())
                    futures.append(send_task)
                except queue.Empty:
                    pass

                done, pending = await asyncio.wait(
                    futures,
                    return_when=asyncio.FIRST_COMPLETED)

                if recv_task in done:
                    data = recv_task.result()
                    recv_queue.put(data)
                    print(data)
                else:
                    recv_task.cancel()
        except:
            print("Disconnected")
            self._nodes.remove(websocket)
            del self._queues[websocket]

    def _start_server_thread(self):
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        start_server = websockets.serve(self._server, '0.0.0.0', self._port)
        loop.run_until_complete(start_server)
        loop.run_forever()

    def _start_client_thread(self, ip):
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        loop.run_until_complete(self._client(ip))

    def _worker_thread(self):
        while True:
            for q in list(self._queues.values()):
                try:
                    data = q[0].get_nowait()
                    print('\nData: ', data, '\n')
                except queue.Empty:
                    pass

