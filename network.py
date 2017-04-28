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
        self._nodes = set()
        self._queues = {}
        self._events = None
        self._sever_loop = None

        self._server_thread = threading.Thread(target=self._start_server_thread,
                                               daemon=True)

    def start(self):
        """ Starts a thread for the server
        """
        self._server_thread.start()

    def close_connections(self):
        for node in list(self._nodes):
            try:
                asyncio.get_event_loop().run_until_complete(
                    node.close_connection(force=True))
            except RuntimeError:
                pass

    def connect_node(self, ip, port):
        """ Connects server to a node
        """
        threading.Thread(target=self._start_client_thread,
                         args=(ip,port,), daemon=True).start()

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
        await self._socket(websocket, self._server_loop)

    async def _client(self, ip, port, loop):
        """ Connects to a new node
        """
        async with websockets.connect('ws://' + ip + ':' + str(port),
                                      loop=loop) as websocket:
            Events.Instance().notify(EVENTS_TYPE.NEW_CLIENT_CONNECTION,
                                     websocket)
            await self._socket(websocket, loop)

    async def _socket(self, websocket, loop):
        """ Creates two queues. One for sending and one for receiving
        """
        self._nodes.add(websocket)
        recv_queue = janus.Queue(loop=loop)
        send_queue = janus.Queue(loop=loop)
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

        recv_task = asyncio.ensure_future(recv(), loop=loop)
        send_task = asyncio.ensure_future(send(), loop=loop)
        Events.Instance().notify(EVENTS_TYPE.CONNECTION_READY, websocket)
        await asyncio.wait([recv_task, send_task], loop=loop,
                           return_when=asyncio.FIRST_COMPLETED)

        print(info("Disconnected"))
        self._nodes.remove(websocket)
        del self._queues[websocket]
        Events.Instance().notify(EVENTS_TYPE.CONNECTION_CLOSED, websocket)

    def _start_server_thread(self):
        """ Starts a server thread and sets it to run until completion
        """
        asyncio.set_event_loop(None)
        self._server_loop = asyncio.new_event_loop()
        start_server = websockets.serve(self._server, '0.0.0.0',
                                        self._port, loop=self._server_loop)
        self._server_loop.run_until_complete(start_server)
        self._server_loop.run_forever()

    def _start_client_thread(self, ip, port):
        """ Starts a client thread and sets it to run until completion
        """
        try:
            asyncio.set_event_loop(None)
            loop = asyncio.new_event_loop()
            loop.run_until_complete(self._client(ip, port, loop))
        except:
            print(fail('fatal error'))
            raise
