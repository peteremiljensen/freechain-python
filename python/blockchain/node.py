import threading
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
        """ Node class constructor
        """

        self._network = Network(port)

        self._chain = Chain()
        self._loaf_pool = {}
        self._loaf_pool_lock = threading.RLock()

        self._events_thread = threading.Thread(target=self._start_events_thread,
                                               daemon=True)
        self._events_thread.start()
        self._worker_thread = threading.Thread(target=self._worker_thread,
                                               daemon=True)

    def start(self):
        """ Starts the node by creating a worker thread and a network thread """
        self._network.start()
        self._worker_thread.start()

        def new_connection_callback(websocket):
            self._get_length(websocket)
        Events.Instance().register_callback(EVENTS_TYPE.NEW_CLIENT_CONNECTION,
                                            new_connection_callback)

    def connect_node(self, ip):
        """ Connects to another node through its IP address """
        self._network.connect_node(ip)

    def add_loaf(self, loaf):
        with self._loaf_pool_lock:
            if loaf.validate() and not loaf.get_hash() in self._loaf_pool:
                self._loaf_pool[loaf.get_hash()] = loaf
                return True
            else:
                return False

    def add_block(self, block):
        return self._chain.add_block(block)

    def broadcast_loaf(self, loaf):
        """ Validates a loaf. If it is validated, it puts the loaves hash in
            the loaf pool and broadcasts it to all connected nodes
        """
        self._network.broadcast(
            self._json({'type': 'request',
                        'function': FUNCTIONS.BROADCAST_LOAF,
                        'loaf': loaf}))

    def broadcast_block(self, block):
        self._network.broadcast(
            self._json({'type': 'request',
                        'function': FUNCTIONS.BROADCAST_BLOCK,
                        'block': block}))

    def mine(self):
        with self._loaf_pool_lock:
            loaves_total = 0
            loaves_hash = []
            loaves = []
            for loaf_hash in list(self._loaf_pool.keys()):
                loaves_hash.append(loaf_hash)
                loaves_total += 1
                if loaves_total == 1000:
                    break
            for h in loaves_hash:
                loaves.append(self._loaf_pool[h])

            block = self._chain.mine_block(loaves)

            if block.validate():
                for loaf_hash in loaves_hash:
                    del self._loaf_pool[loaf_hash]
                return block
            else:
                print(fail('block could not be mined'))
                return None

    def _get_length(self, websocket):
        """ Requests the length of the blockchain from a node """

        self._network.send(websocket, self._json(
            {'type': 'request',
             'function': FUNCTIONS.GET_LENGTH}))

    def _get_blocks(self, websocket, offset, length):
        """ Requests  missing blocks from a node """

        self._network.send(websocket, self._json(
            {'type': 'request',
             'function': FUNCTIONS.GET_BLOCKS,
             'offset': offset,
             'length': length}))

    def _start_events_thread(self):
        """ Starts an event thread that runs untill completion """
        try:
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            events = Events.Instance()
            loop.run_until_complete(events.start())
        except:
            print(fail('fatal error regarding events'))
            raise

    def _worker_thread(self):
        """ Starts the worker thread, which listens for requests from other
            nodes in the network.
        """
        while True:
            for websocket in list(self._network.get_queues().keys()):
                try:
                    raw_data = self._network.recv_nowait(websocket)
                    message = json.loads(raw_data.decode('utf-8'))

                    if message['type'] == 'error':
                        desc = 'No description'
                        if 'description' in message:
                            desc = message['description']
                        print(fail('Error received: ' + desc))
                    elif message['function'] == FUNCTIONS.GET_LENGTH:
                        self._handle_get_length(message, websocket)
                    elif message['function'] == FUNCTIONS.GET_BLOCKS:
                        self._handle_get_blocks(message, websocket)
                    elif message['function'] == FUNCTIONS.BROADCAST_LOAF:
                        self._handle_broadcast_loaf(message)
                    elif message['function'] == FUNCTIONS.BROADCAST_BLOCK:
                        self._handle_broadcast_block(message, websocket)
                    else:
                        self._network.send(
                            websocket, self._json({'type': 'error',
                                                   'description':
                                                   'Unsupported function'}))

                except AttributeError:
                    response = self._json({'type': 'error',
                                           'description': 'Request not ' + \
                                           'encoded correctly as UTF-8'})
                    self._network.send(websocket, response)
                except SyncQueueEmpty:
                    pass
                except:
                    print(fail("fatal error"))
                    raise
            time.sleep(0.05)

    def _handle_get_length(self, message, websocket):
        """ Reads a request for the length of the blockchain. If local
            blockchain is shorter, it sends a request for missing blocks
        """
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
                                 response_length - chain_length)
            else:
                print(info('Keeping local blocks'))

        else:
            self._network.send(
                websocket,
                self._json({'type': 'error',
                            'description': 'type is not supported'}))

    def _handle_get_blocks(self, message, websocket):
        """ Reads a request for missing blocks and sends them if local chain
            is longer
        """
        if message['type'] == 'request':
            if self._chain.get_length() >= \
               message['offset'] + message['length']:
                blocks = []
                for i in range(message['length']):
                    blocks.append(self._chain.get_block(i + message['offset']))
                response = self._json({'type': 'response',
                                       'function': FUNCTIONS.GET_BLOCKS,
                                       'blocks': blocks})
                self._network.send(websocket, response)
            else:
                self._network.send(
                    websocket,
                    self._json({'type': 'error',
                                'description': 'requested length is ' + \
                                'longer than chain'}))

        elif message['type'] == 'response':
            blocks = []
            for block_dict in message['blocks']:
                blocks.append(Block.create_block_from_dict(block_dict))
            for block in blocks:
                if not self._chain.add_block(block):
                    print(fail('block cannot be added'))
                    return
            print(info('blocks succesfully added to blockchain'))

        else:
            self._network.send(
                websocket,
                self._json({'type': 'error',
                            'description': 'type is not supported'}))

    def _handle_broadcast_loaf(self, message):
        """ Receives and validates a loaf. If loaf is not validated,
            an error message is displayed. If loaf is validated, it checks
            whether loaf already exists in the local loaf pool. If it does not
            exist in the loaf pool, it adds the loaf to the loaf pool and
            broadcasts the loaf to all connected nodes.
        """
        loaf = Loaf.create_loaf_from_dict(message['loaf'])
        with self._loaf_pool_lock:
            if not loaf.get_hash() in self._loaf_pool:
                if self.add_loaf(loaf):
                    self.broadcast_loaf(loaf)
                    print(info('Received loaf and forwarding it'))
                else:
                    print(fail('Received loaf could not validate'))

    def _handle_broadcast_block(self, message, websocket):
        block = Block.create_block_from_dict(message['block'])

        if block.get_height() > self._chain.get_length():
            self._get_length(websocket)
        elif block.get_height() < self._chain.get_length():
            return
        elif self.add_block(block):
            with self._loaf_pool_lock:
                print(info('block succesfully added'))
                for loaf in block.get_loaves():
                    try:
                        del self._loaf_pool[loaf.get_hash()]
                    except KeyError:
                        pass
            self.broadcast_block(block)
        else:
            print(fail('block could not be added'))

    @staticmethod
    def _json(dictio):
        """ Serializes object to a JSON formatted string, encodes to utf-8
            and returns
        """
        return json.dumps(dictio, cls=BlockEncoder).encode('utf-8')
