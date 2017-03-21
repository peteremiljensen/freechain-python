import hashlib
import base64
import datetime
import json

class Loaf():
    def __init__(self, id, data):
        self._loaf = {}
        self._loaf['id'] = id
        self._loaf['data'] = data
        self._loaf['timestamp'] = str(datetime.datetime.now())
        dump = self.json()
        self._loaf['hash'] = hashlib.sha256(dump).hexdigest()

    def json(self):
        return json.dumps(self._loaf, sort_keys=True).encode('utf-8')

    @staticmethod
    def create_loaf_from_json(json):
        
        return True


