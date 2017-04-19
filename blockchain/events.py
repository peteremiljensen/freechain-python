import asyncio
import threading
import janus

from asyncio import QueueEmpty as AsyncQueueEmpty

from blockchain.singleton import Singleton

#   _____                _
#  |  ___|              | |
#  | |____   _____ _ __ | |_ ___
#  |  __\ \ / / _ \ '_ \| __/ __|
#  | |___\ V /  __/ | | | |_\__ \
#  \____/ \_/ \___|_| |_|\__|___/
#

@Singleton
class Events():
    def __init__(self):
        """ Event class constructor
        """
        self._loop = asyncio.new_event_loop()
        self._queue = janus.Queue(loop=self._loop)
        self._callback = {}
        self._callback_lock = threading.RLock()

    def start(self):
        while True:
            event_tuple = self._queue.sync_q.get()
            with self._callback_lock:
                event = event_tuple[0]
                if event in self._callback:
                    for func in self._callback[event]:
                        func(event_tuple[1])

    def register_callback(self, event, callback):
        with self._callback_lock:
            if event in self._callback:
                self._callback[event].append(callback)
            else:
                self._callback[event] = [callback]

    def notify(self, event, data):
        self._queue.sync_q.put((event, data))

