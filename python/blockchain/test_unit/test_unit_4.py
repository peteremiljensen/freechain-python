import unittest
import asyncio
import threading
from .. import events

class TestEventsMethods(unittest.TestCase):

    def setUp(self):
        self.e = events.Events.Instance()
        self.assertion = False
        self.data = ""
        self.assertion_2 = False
        self.sema = threading.Semaphore(0)
        self.sema_2 = threading.Semaphore(0)
        self.sema_3 = threading.Semaphore(0)

        def callback(data):
            if data == 'data':
                self.assertion = True
                self.data = data
                self.sema.release()
        def callback_2(data):
            if data == 'data_2':
                self.sema_3.acquire(timeout=20)
                self.assertion_2 = True
                self.data = data
                self.sema_2.release()
        self.e.register_callback("test", callback)
        self.e.register_callback("test", callback_2)
        self.e.notify("test", "data")
        self.e.notify("test", "data_2")

        self.thread = threading.Thread(target=self.e.start, daemon=True)
        self.thread.start()

    def test_callback(self):
        self.sema.acquire(timeout=20)
        self.assertTrue(self.assertion)
        self.assertEqual(self.data, "data")
        self.sema_3.release()
        self.sema_2.acquire(timeout=20)
        self.assertTrue(self.assertion_2)
        self.assertEqual(self.data, "data_2")

if __name__ == '__main__':
    unittest.main()
