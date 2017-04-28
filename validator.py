from blockchain.singleton import Singleton

@Singleton
class Validator():
    def __init__(self):
        self._loaf_validator  = lambda l:  True
        self._block_validator = lambda b:  True
        self._consensus_check = lambda l, r: False
        self._consensus       = lambda c1, c2:  c1

    def attach_loaf_validator(self, function):
        self._loaf_validator = function

    def attach_block_validator(self, function):
        self._block_validator = function

    def attach_consensus_check(self, function):
        self._consensus_check = function

    def attach_consensus(self, function):
        self._consensus = function

    def validate_loaf(self, loaf):
        return self._loaf_validator(loaf)

    def validate_block(self, block):
        return self._block_validator(block)

    def consensus_check(self, local_length, rec_length):
        return self._consensus_check(local_length, rec_length)

    def consensus(self, chain1, chain2):
        return self._consensus(chain1, chain2)
