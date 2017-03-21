import hashlib
import base64
import datetime
import json

class Loaf():
    def __init__(self, data, timestamp=None, hash=None):
        self._loaf = {}
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

    def get_hash(self):
        return self._block['hash']

    def calculate_hash(self):
        hash_tmp = self._loaf['hash']
        del self._loaf['hash']
        hash_calc = hashlib.sha256(self.json()).hexdigest()
        self._loaf['hash'] = hash_tmp
        return hash_calc

    def validate(self):
        hash_calc = self.calculate_hash()
        return self._loaf['hash'] == hash_calc

    @staticmethod
    def create_loaf_from_json(json_string):
        dump = json.loads(json_string)
        return Loaf(dump['data'], dump['timestamp'], dump['hash'])


class LoafEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, Loaf):
            return obj._loaf
        return json.JSONEncoder.default(self, obj)
