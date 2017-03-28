import asyncio
import threading
import janus

class Events():
    def __init__(self):
        self._loop = asyncio.get_event_loop()
        self._queue = janus.Queue(loop=self._loop)
        self._callback = {}
        self._callback_lock = threading.RLock()

    async def start(self):
        return

    def register_callback(event, callback):
        with self._callback_lock:
            if event in self._callback:
                self._callback[event].append(callback)
            else:
                self._callback[event] = [callback]
