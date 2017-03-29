import asyncio
import janus
import time
import json

from blockchain.events import Events
from blockchain.network import Network
from blockchain.chain import *
from blockchain.loaf import Loaf
from blockchain.block import Block

from blockchain.common import *

from queue import Empty as SyncQueueEmpty

#   _   _           _
#  | \ | |         | |
#  |  \| | ___   __| | ___
#  | . ` |/ _ \ / _` |/ _ \
#  | |\  | (_) | (_| |  __/
#  \_| \_/\___/ \__,_|\___|
#

class Node():
    def __init__(self, port):
        self._network = Network(port)

        self._chain = Chain()
        self._loaf_pool = {}

        self._events_thread = threading.Thread(target=self._start_events_thread,
                                               daemon=True)
        self._events_thread.start()
        self._worker_thread = threading.Thread(target=self._worker_thread,
                                               daemon=True)

    def start(self):
        self._network.start()
        self._worker_thread.start()

        def new_connection_callback(websocket):
            self._get_length(websocket)
        Events.Instance().register_callback(EVENTS_TYPE.NEW_CLIENT_CONNECTION,
                                            new_connection_callback)

    def connect_node(self, ip):
        self._network.connect_node(ip)

    def broadcast_loaf(self, loaf):
        if loaf.validate():
            self._loaf_pool[loaf.get_hash()] = loaf
            self._network.broadcast(
                self._json({'type': 'request',
                            'function': FUNCTIONS.BROADCAST_LOAF,
                            'loaf': loaf}))

    def _get_length(self, websocket):
        self._network.send(websocket, self._json(
            {'type': 'request',
             'function': FUNCTIONS.GET_LENGTH}))

    def _get_blocks(self, websocket, offset, length):
        self._network.send(websocket, self._json(
            {'type': 'request',
             'function': FUNCTIONS.GET_BLOCKS,
             'offset': offset,
             'length': length}))

    def _start_events_thread(self):
        try:
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            events = Events.Instance()
            loop.run_until_complete(events.start())
        except:
            print(fail('fatal error regarding events'))
            raise

    def _worker_thread(self):
        while True:
            for websocket in list(self._network.get_queues().keys()):
                try:
                    raw_data = self._network.recv_nowait(websocket)
                    message = json.loads(raw_data.decode('utf-8'))

                    if message['function'] == FUNCTIONS.GET_LENGTH:
                        self._response_get_length(message, websocket)
                    elif message['function'] == FUNCTIONS.GET_BLOCKS:
                        self._response_get_blocks(message, websocket)
                    elif message['function'] == FUNCTIONS.BROADCAST_LOAF:
                        self._response_broadcast_loaf(message)

                except AttributeError:
                    response = self._json({'type': 'error',
                                           'decription': 'Request not ' + \
                                           'encoded correctly as UTF-8'})
                    self._network.send(websocket, response)
                except SyncQueueEmpty:
                    pass
                except:
                    print(fail("fatal error"))
                    raise
            time.sleep(0.05)

    def _response_get_length(self, message, websocket):
        if message['type'] == 'request':
            chain_length = self._chain.get_length()
            response = self._json({'type': 'response',
                                   'function': FUNCTIONS.GET_LENGTH,
                                   'length': chain_length})
            self._network.send(websocket, response)
        elif message['type'] == 'response':
            chain_length = self._chain.get_length()
            response_length = message['length']
            print(info('Recieved blockchain length is: ' +
                       str(response_length)))
            print(info('local block length is : ' +
                       str(chain_length)))
            if response_length > chain_length:
                print(info('local blockchain is shorter, ' +
                           'querying missing blocks'))
                self._get_blocks(websocket, chain_length,
                                 (response_length - chain_length))
            else:
                print(info('Keeping local blocks'))
        elif message['type'] == 'error':
            print(fail('Error received'))
        else:
            self._network.send(websocket, self._json({'type': 'error'}))

    def _response_get_blocks(self, message, websocket):
        if message['type'] == 'request':
            if self._chain.get_length() < \
               message['offset'] + message['length'] - 1:
                blocks = []
                for i in range(message['length']):
                    blocks.append(self._chain.get_block(i + message['offset']))
                response = self._json({'type': 'response',
                                       'function': FUNCTION.GET_BLOCKS,
                                       'blocks': blocks})
                self._network.send(websocket, response)
            else:
                self._network.send(websocket, self._json({'type': 'error'}))

    def _response_broadcast_loaf(self, message):
        loaf = Loaf.create_loaf_from_dict(message['loaf'])
        if loaf.validate():
            if not loaf.get_hash() in self._loaf_pool:
                self._loaf_pool[loaf.get_hash()] = loaf
                self.broadcast_loaf(loaf)
                print(info('Received loaf and forwarding it'))
        else:
            print(warning('Received loaf could not validate'))

    @staticmethod
    def _json(dictio):
        return json.dumps(dictio, cls=BlockEncoder).encode('utf-8')
