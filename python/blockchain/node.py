import threading
import asyncio
import websockets
import queue
import time
import json
from concurrent.futures import ThreadPoolExecutor

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

    def get_length(self):
        self.broadcast(json.dumps({'type': 'request',
                                    'function': 'get_length'}))
    def broadcast(self, data):
        for queue in list(self._queues.values()):
            queue[1].put(data)

    async def _server(self, websocket, path):
        await self._socket(websocket)

    async def _client(self, ip):
        async with websockets.connect('ws://' + ip + ':9000') as websocket:
            await self._socket(websocket)

    async def _socket(self, websocket):
        executor = ThreadPoolExecutor(1)
        loop = asyncio.get_event_loop()
        self._nodes.add(websocket)
        recv_queue = queue.Queue()
        send_queue = queue.Queue()
        self._queues[websocket] = (recv_queue, send_queue)
        try:
            while True:
                recv_task = asyncio.ensure_future(websocket.recv())
                send_task = asyncio.ensure_future(loop.run_in_executor(executor, send_queue.get))

                done, pending = await asyncio.wait(
                    [recv_task, send_task],
                    return_when=asyncio.FIRST_COMPLETED)

                if recv_task in done:
                    data = recv_task.result()
                    recv_queue.put(data)
                else:
                    recv_task.cancel()

                if send_task in done:
                    data = send_task.result()
                    await websocket.send(data)
                else:
                    send_task.cancel()
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
                    raw_data = q[0].get_nowait()
                    message = json.loads(raw_data)
                    if message['type'] == 'request' and \
                       message['function'] == 'get_length':
                        chain_length = self._chain.get_length()
                        response = json.dumps({'type': 'response',
                                               'function': 'get_length',
                                               'length': chain_length})
                        q[1].put(response)
                    elif message['type'] == 'response' and \
                         message['function'] == 'get_length':
                        print('Recieved blockchain length is: ',
                              message['length'])
                    elif message['type'] == 'error':
                        print('Received error')
                    else:
                        q[1].put(json.dumps({'type': 'error'}))
                except queue.Empty:
                    pass
                except:
                    print(sys.exc_info()[0])
                    pass
            time.sleep(0.01)
