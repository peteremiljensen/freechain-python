import unittest
import asyncio
import threading
from .. import events

class TestEventsMethods(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        cls.e = events.Events.Instance()
        cls.assertion = False
        cls.data = ""
        cls.assertion_2 = False
        cls.sema = threading.Semaphore(0)
        cls.sema_2 = threading.Semaphore(0)
        cls.sema_3 = threading.Semaphore(0)

        def callback(data):
            if data == 'data':
                cls.assertion = True
                cls.data = data
                cls.sema.release()
        def callback_2(data):
            if data == 'data_2':
                cls.sema_2.acquire(timeout=20)
                cls.assertion_2 = True
                cls.data = data
                cls.sema_3.release()
        cls.e.register_callback("test", callback)
        cls.e.register_callback("test", callback_2)
        cls.e.notify("test", "data")
        cls.e.notify("test", "data_2")

        cls.thread = threading.Thread(target=cls.e.start, daemon=True)
        cls.thread.start()

    def test_callback(self):
        self.sema.acquire(timeout=20)
        self.assertTrue(self.assertion)
        self.assertEqual(self.data, "data")
        self.sema_2.release()
        self.sema_3.acquire(timeout=20)
        self.assertTrue(self.assertion_2)
        self.assertEqual(self.data, "data_2")

if __name__ == '__main__':
    unittest.main()
