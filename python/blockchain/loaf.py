import hashlib
import base64
import datetime
import json

class Loaf():
    def __init__(self, id, data, timestamp=None, hash=None):
        self._loaf = {}
        self._loaf['id'] = id
        self._loaf['data'] = data
        if timestamp == None:
            self._loaf['timestamp'] = str(datetime.datetime.now())
        else:
            self._loaf['timestamp'] = timestamp
        if hash == None:
            self._loaf['hash'] = hashlib.sha256(self.json()).hexdigest()
        else:
            self._loaf['hash'] = hash

    def json(self):
        return json.dumps(self._loaf, sort_keys=True).encode('utf-8')

    def validate(self):
        hash_tmp = self._loaf['hash']
        del self._loaf['hash']
        hash_calc = hashlib.sha256(self.json()).hexdigest()
        self._loaf['hash'] = hash_tmp
        return hash_tmp == hash_calc

    @staticmethod
    def create_loaf_from_json(json_string):
        dump = json.loads(json_string)
        return Loaf(dump['id'], dump['data'], dump['timestamp'], dump['hash'])


