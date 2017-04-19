import unittest
import asyncio
import threading, time
from .. import events

class TestEventsMethods(unittest.TestCase):

    def setUp(self):
        self.e = events.Events.Instance()
        self.assertion = False
        self.data = ""
        self.sema = threading.Semaphore(0)

        def callback(data):
            self.sema.release()
            self.assertion = True
            self.data = data
        self.e.register_callback("test", callback)
        self.e.notify("test", "data")

        self.thread = threading.Thread(target=self.thread, daemon=True)
        self.thread.start()

    def thread(self):
        loop = asyncio.new_event_loop()
        loop.run_until_complete(self.e.start())

    def test_callback(self):
        self.sema.acquire()
        self.assertTrue(self.assertion)
        self.assertEqual(self.data, "data")

if __name__ == '__main__':
    unittest.main()
