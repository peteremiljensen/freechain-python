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
        """ Network class constructor
        """
        self._port = port
        self._queues = {}
        self._events = None
        self._loop = asyncio.get_event_loop()

    def start(self):
        """ Starts a thread for the server
        """
        self._start_server()

    def connect_node(self, ip, port):
        """ Connects server to a node
        """
        self._start_client(ip, port)

    def broadcast(self, data):
        """ Broadcasts data to connected nodes
        """
        for queue in list(self._queues.values()):
            queue[1].sync_q.put(data)

    def send(self, websocket, data):
        """ Sends data to specific node
        """
        if websocket in self._queues:
            self._queues[websocket][1].sync_q.put(data)

    def recv_nowait(self, websocket):
        """ Returns contents of queue. If queue is empty, raises exception
        """
        return self._queues[websocket][0].sync_q.get_nowait()

    def get_queues(self):
        """ Returns queues
        """
        return self._queues

    async def _server(self, websocket, path):
        """ Waits for _socket to be called
        """
        await self._socket(websocket)

    async def _client(self, websocket):
        """ Connects to a new node
        """
        #Events.Instance().notify(EVENTS_TYPE.NEW_CLIENT_CONNECTION,
        #                         websocket)
        await self._socket(websocket)

    async def _socket(self, websocket):
        """ Creates two queues. One for sending and one for receiving
        """
        data = await websocket.recv()
        await websocket.send(data)
        '''self._nodes.add(websocket)
        recv_queue = janus.Queue()
        send_queue = janus.Queue()
        self._queues[websocket] = (recv_queue, send_queue)
        async def recv():
            try:
                while True:
                    data = await websocket.recv()
                    await recv_queue.async_q.put(data)
            except websockets.exceptions.ConnectionClosed:
                pass
        async def send():
            try:
                while True:
                    data = await send_queue.async_q.get()
                    await websocket.send(data)
            except websockets.exceptions.ConnectionClosed:
                pass

        recv_task = asyncio.ensure_future(recv())
        send_task = asyncio.ensure_future(send())
        await asyncio.wait([recv_task, send_task],
                           return_when=asyncio.FIRST_COMPLETED)

        print(info("Disconnected"))
        self._nodes.remove(websocket)
        del self._queues[websocket]'''

    def _start_server(self):
        """ Starts a server thread and sets it to run until completion
        """
        server = websockets.serve(self._server, '0.0.0.0',
                                  self._port)
        self._loop.run_until_complete(server)

    def _start_client(self, ip, port):
        """ Starts a client thread and sets it to run until completion
        """
        client = websockets.connect('ws://' + ip + ':' + str(port))
        websocket = self._loop.run_until_complete(client)
        self._loop.run_until_complete(websocket.send("Hello!"))
        reply = self._loop.run_until_complete(websocket.recv())
        print(reply)
