import asyncio
import janus
import time
import json
import sys

from blockchain.network import Network
from blockchain.chain import *
from blockchain.loaf import Loaf
from blockchain.block import Block

from queue import Empty as SyncQueueEmpty

def info(string):
    return('\033[92m' + string + '\033[0m')
def warning(string):
    return('\033[93m*** ' + string + '\033[0m')
def fail(string):
    return('\033[91m*** ' + string + '\033[0m')

class Node():
    def __init__(self, port):
        self._network = Network(port)

        self._chain = Chain()
        self._loaf_pool = {}

        self._worker_thread = threading.Thread(target=self._worker_thread,
                                               daemon=True)

    def start(self):
        self._network.start()
        self._worker_thread.start()

    def connect_node(self, ip):
        self._network.connect_node(ip)

    def broadcast_loaf(self, loaf):
        if loaf.validate():
            self._loaf_pool[loaf.get_hash()] = loaf
            self._network.broadcast(self._json({'type': 'request',
                                                'function': 'broadcast_loaf',
                                                'loaf': loaf}))

    def _get_length(self, websocket):
        self._network.send(websocket, self._json({'type': 'request',
                                                  'function': 'get_length'}))

    def _worker_thread(self):
        queues = self._network.get_queues()
        while True:
            for q in list(queues.values()):
                try:
                    raw_data = q[0].sync_q.get_nowait()
                    message = json.loads(raw_data.decode('utf-8'))

                    if message['function'] == 'get_length':
                        self._function_get_length(q, message)
                    elif message['function'] == 'broadcast_loaf':
                        self._function_broadcast_loaf(message)

                    q[0].sync_q.task_done()
                except SyncQueueEmpty:
                    pass
                except:
                    print(fail("fatal error"))
                    raise
            time.sleep(0.01)

    def _function_get_length(self, q, message):
        if message['type'] == 'request':
            chain_length = self._chain.get_length()
            response = json.dumps({'type': 'response',
                                   'function': 'get_length',
                                   'length': chain_length})
            q[1].sync_q.put(response)
        elif message['type'] == 'response':
            print(info('Recieved blockchain length is: ',
                       message['length']))
        elif message['type'] == 'error':
            print(fail('Error received'))
        else:
            q[1].sync_q.put(json.dumps({'type': 'error'}))

    def _function_broadcast_loaf(self, message):
        loaf = Loaf.create_loaf_from_dict(message['loaf'])
        if loaf.validate():
            if not loaf.get_hash() in self._loaf_pool:
                self._loaf_pool[loaf.get_hash()] = loaf
                self.broadcast_loaf(loaf)
                print(info('Received loaf and forwarding it'))
        else:
            print(warning('Received loaf could not validate'))

    @staticmethod
    def _json(dic):
        return json.dumps(dic, cls=BlockEncoder).encode('utf-8')
