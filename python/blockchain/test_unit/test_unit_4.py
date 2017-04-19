import unittest
import asyncio
import threading, time
from .. import events

class TestEventsMethods(unittest.TestCase):

    def setUp(self):
        self.e = events.Events.Instance()
        self.assertion = False
        self.data = ""
        self.assertion_2 = False
        self.sema = threading.Semaphore(0)
        self.sema_2 = threading.Semaphore(0)

        def callback(data):
            self.assertion = True
            self.data = data
            self.sema.release()
        def callback_2(data):
            self.data = data
            self.assertion_2 = True
            self.sema_2.release()
        self.e.register_callback("test", callback)
        self.e.register_callback("test_2", callback_2)
        self.e.notify("test", "data")
        self.e.notify("test_2", "data_2")

        self.thread = threading.Thread(target=self.thread, daemon=True)
        self.thread.start()

    def thread(self):
        try:
            loop = asyncio.new_event_loop()
            loop.run_until_complete(self.e.start())
        except RuntimeError:
            pass

    def test_callback(self):
        self.sema.acquire(timeout=20)
        self.assertTrue(self.assertion)
        self.assertEqual(self.data, "data")
        self.sema_2.acquire(timeout=20)
        self.assertTrue(self.assertion_2)
        self.assertEqual(self.data, "data_2")

if __name__ == '__main__':
    unittest.main()
