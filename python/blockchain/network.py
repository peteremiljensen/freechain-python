import threading
import asyncio
import janus
from autobahn.asyncio.websocket import WebSocketServerProtocol, \
    WebSocketServerFactory, WebSocketClientProtocol, WebSocketClientFactory


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

        self._server_thread = threading.Thread(target=self._start_server_thread,
                                               daemon=True)

    def start(self):
        """ Starts a thread for the server
        """
        self._server_thread.start()

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

    def _start_server_thread(self):
        """ Starts a server thread and sets it to run until completion
        """
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)

        factory = WebSocketServerFactory('ws://0.0.0.0:'+str(self._port))
        factory.protocol = ServerProtocol
        coro = loop.create_server(factory, '0.0.0.0', self._port)
        server = loop.run_until_complete(coro)

        try:
            loop.run_forever()
        except KeyboardInterrupt:
            pass
        finally:
            server.close()
            loop.close()

    def _start_client_thread(self, ip, port):
        """ Starts a client thread and sets it to run until completion
        """
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)

        factory = WebSocketClientFactory('ws://'+ip+':'+str(port))
        factory.protocol = ClientProtocol
        loop = asyncio.get_event_loop()
        coro = loop.create_connection(factory, ip, port)
        loop.run_until_complete(coro)
        loop.run_forever()
        loop.close()

    def _onConnect(self, response):
        print("Connection")

class ServerProtocol(WebSocketServerProtocol):
    def __init__(self, network):
        super().__init__()
        self._network = network

    def onConnect(self, response):
        self._network._onConnect(response)


class ClientProtocol(WebSocketClientProtocol):
    def __init__(self, network):
        super().__init__()
        self._network = network

    def onConnect(self, response):
        self._network._onConnect(response)


