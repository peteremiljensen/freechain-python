import threading
import asyncio
import janus
import websockets

from blockchain.events import Events
from blockchain.common import *

#   _   _      _                      _
#  | \ | |    | |                    | |
#  |  \| | ___| |___      _____  _ __| | __
#  | . ` |/ _ \ __\ \ /\ / / _ \| '__| |/ /
#  | |\  |  __/ |_ \ V  V / (_) | |  |   <
#  \_| \_/\___|\__| \_/\_/ \___/|_|  |_|\_\
#

class Network():
    def __init__(self, port):
        self._port = port
        self._nodes = set()
        self._queues = {}
        self._events = None

        self._server_thread = threading.Thread(target=self._start_server_thread,
                                               daemon=True)

    def start(self):
        self._server_thread.start()

    def connect_node(self, ip):
        threading.Thread(target=self._start_client_thread,
                         args=(ip,), daemon=True).start()

    def broadcast(self, data):
        for queue in list(self._queues.values()):
            queue[1].sync_q.put(data)

    def send(self, websocket, data):
        if websocket in self._queues:
            self._queues[websocket][1].sync_q.put(data)

    def get_queues(self):
        return self._queues

    async def _server(self, websocket, path):
        await self._socket(websocket)

    async def _client(self, ip):
        async with websockets.connect('ws://' + ip + ':' + str(self._port)) \
                   as websocket:
            await self._socket(websocket)

    async def _socket(self, websocket):
        Events.Instance().notify(EVENTS_TYPE.NEW_CONNECTION, websocket)
        loop = asyncio.get_event_loop()
        self._nodes.add(websocket)
        recv_queue = janus.Queue(loop=loop)
        send_queue = janus.Queue(loop=loop)
        self._queues[websocket] = (recv_queue, send_queue)
        try:
            while True:
                recv_task = asyncio.ensure_future(websocket.recv())
                send_task = asyncio.ensure_future(send_queue.async_q.get())

                done, pending = await asyncio.wait(
                    [recv_task, send_task],
                    return_when=asyncio.FIRST_COMPLETED)

                if recv_task in done:
                    data = recv_task.result()
                    await recv_queue.async_q.put(data)
                else:
                    recv_task.cancel()

                if send_task in done:
                    data = send_task.result()
                    await websocket.send(data)
                    send_queue.async_q.task_done()
                else:
                    send_task.cancel()
        except websockets.exceptions.ConnectionClosed:
            pass
        finally:
            print(info("Disconnected"))
            self._nodes.remove(websocket)
            del self._queues[websocket]

    def _start_server_thread(self):
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        start_server = websockets.serve(self._server, '0.0.0.0', self._port)
        loop.run_until_complete(start_server)
        loop.run_forever()

    def _start_client_thread(self, ip):
        try:
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            loop.run_until_complete(self._client(ip))
        except:
            print(fail('fatal error'))
            raise

