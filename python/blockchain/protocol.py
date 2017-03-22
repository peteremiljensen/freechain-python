from autobahn.asyncio.websocket import WebSocketServerProtocol, \
    WebSocketServerFactory
from autobahn.asyncio.websocket import WebSocketClientProtocol, \
    WebSocketClientFactory

from blockchain.node import Node

class ServerProtocol(WebSocketServerProtocol):

    def onConnect(self, request):
        print("Client connecting: {0}".format(request.peer))
        Node().broadcast_loaf(2)

    def onOpen(self):
        print("WebSocket connection open.")
        self._node.broadcast_loaf(2)

    def onMessage(self, payload, isBinary):
        if isBinary:
            print("Binary message received: {0} bytes".format(len(payload)))
        else:
            print("Text message received: {0}".format(payload.decode('utf8')))

        # echo back message verbatim
        self.sendMessage(payload, isBinary)

    def onClose(self, wasClean, code, reason):
        print("WebSocket connection closed: {0}".format(reason))

