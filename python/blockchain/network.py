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
        #self._start_server()

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

    async def _socket(self, websocket, path):
        """ Creates two queues. One for sending and one for receiving
        """
        print("_socket")

    def _start_server(self):
        """ Starts a server thread and sets it to run until completion
        """
        start_server = websockets.serve(self._socket, 'localhost', 9000)

        self._loop.run_until_complete(start_server)
        self._loop.run_forever()

    async def _client(self):
        async with websockets.connect('ws://localhost:9000/') as websocket:
            await self._socket(websocket, '/')
            #raise Exception("Catch me!")

    async def _client_runner(self):
        tasks = [self._client() for _ in range(10)]
        done, pending = await asyncio.wait(tasks, return_when=asyncio.FIRST_EXCEPTION)

        if pending:
            for t in pending:
                t.cancel()
            await asyncio.wait(pending)

        for t in done:
            t.exception()  # Retrieve any exception.

        print ("_client_runner done")

    def _start_client(self, ip, port):
        """ Starts a client thread and sets it to run until completion
        """
        self._loop.run_until_complete(self._client_runner())
        #print(websocket)
