import hashlib
import datetime
import json

from blochain.validator import Validator

#   _                  __
#  | |                / _|
#  | |     ___   __ _| |_
#  | |    / _ \ / _` |  _|
#  | |___| (_) | (_| | |
#  \_____/\___/ \__,_|_|
#

class Loaf():
    def __init__(self, data, timestamp=None, hash=None):
        """ Loaf class constructor. If timestamp and hash are not given,
            sets timestamp to current time and creates a hash.
        """
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
        """ Serializes loaf to a JSON formatted string, encodes to utf-8
            and returns
        """
        return json.dumps(self._loaf, sort_keys=True).encode('utf-8')

    def get_hash(self):
        """ Returns hash of loaf """
        return self._loaf['hash']

    def calculate_hash(self):
        """ Calculates the same hash of loaf object """
        hash_tmp = self._loaf['hash']
        del self._loaf['hash']
        hash_calc = hashlib.sha256(self.json()).hexdigest()
        self._loaf['hash'] = hash_tmp
        return hash_calc

    def validate(self):
        """ Calculates loaf hash and compares it to current hash.
        returns True if they are the same
        """
        return Validator.Instance().validate_loaf(self)

    @staticmethod
    def create_loaf_from_dict(dictio):
        """ Returns a loaf object created from given dictionary """
        return Loaf(dictio['data'], dictio['timestamp'], dictio['hash'])

class LoafEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, Loaf):
            return obj._loaf
        return json.JSONEncoder.default(self, obj)
