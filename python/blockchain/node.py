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
        """ Node class constructor """

        self._network = Network(port)

        self._chain = Chain()
        self._loaf_pool = {}

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

    def broadcast_loaf(self, loaf):
        """ Validates a loaf. If it is validated, it puts the loafs hash in
            the loaf pool and broadcasts it to all connected nodes
        """
        if loaf.validate():
            self._loaf_pool[loaf.get_hash()] = loaf
            self._network.broadcast(
                self._json({'type': 'request',
                            'function': FUNCTIONS.BROADCAST_LOAF,
                            'loaf': loaf}))

    def broadcast_block(self, block):
        if self._chain.add_block(block):
            self._network.broadcast(
                self._json({'type': 'request',
                            'function': FUNCTIONS.BROADCAST_BLOCK,
                            'block': block}))
        else:
            printf(fail('error validating block while trying to broadcast'))

    def mine(self):
        loafs_total = 0
        loafs_hash = []
        loafs = []
        for loaf_hash in list(self._loaf_pool.keys()):
            loafs_hash.append(loaf_hash)
            loafs_total += 1
            if loafs_total == 1000:
                break
        for h in loafs_hash:
            loafs.append(self._loaf_pool[h])
        block = self._chain.mine_block(loafs)
        if block.validate():
            for loaf_hash in loafs_hash:
                del self._loaf_pool[loaf_hash]
            self.broadcast_block(block)
        else:
            print(fail('block could not be mined'))

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
                        print(fail('Error received'))
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
                                           'decription': 'Request not ' + \
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
                                 (response_length - (chain_length - 1)))
            else:
                print(info('Keeping local blocks'))

        else:
            self._network.send(websocket, self._json({'type': 'error'}))

    def _handle_get_blocks(self, message, websocket):
        """ Reads a request for missing blocks and sends them if local chain
            is longer
        """
        if message['type'] == 'request':
            if self._chain.get_length() < message['offset'] + message['length']:
                blocks = []
                for i in range(message['length']):
                    blocks.append(self._chain.get_block(i + message['offset']))
                response = self._json({'type': 'response',
                                       'function': FUNCTION.GET_BLOCKS,
                                       'blocks': blocks})
                self._network.send(websocket, response)
            else:
                self._network.send(websocket, self._json({'type': 'error'}))

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
            self._network.send(websocket, self._json({'type': 'error'}))

    def _handle_broadcast_loaf(self, message):
        """ Receives and validates a loaf. If loaf is not validated,
            an error message is displayed. If loaf is validated, it checks
            whether loaf already exists in the local loaf pool. If it does not
            exist in the loaf pool, it adds the loaf to the loaf pool and
            broadcasts the loaf to all connected nodes.
        """
        loaf = Loaf.create_loaf_from_dict(message['loaf'])
        if loaf.validate():
            if not loaf.get_hash() in self._loaf_pool:
                self._loaf_pool[loaf.get_hash()] = loaf
                self.broadcast_loaf(loaf)
                print(info('Received loaf and forwarding it'))
        else:
            print(warning('Received loaf could not validate'))

    def _handle_broadcast_block(self, message, websocket):
        block = Block.create_block_from_dict()

        if block.get_height() > self._chain.get_length():
            self._get_length(websocket)
        elif block.get_height() < self._chain.get_length():
            return
        elif not self._chain.add_block(block):
            print(fail('block could not be added'))

        print(info('block succesfully added'))
        self.broadcast_block(block)

    @staticmethod
    def _json(dictio):
        """ Serializes object to a JSON formatted string, encodes to utf-8
            and returns
        """
        return json.dumps(dictio, cls=BlockEncoder).encode('utf-8')
