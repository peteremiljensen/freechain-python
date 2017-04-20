from blockchain.singleton import Singleton

@Singleton
class Validator():
    def __init__(self):
        self._loaf_validator  = lambda l: True
        self._block_validator = lambda b: True

    def attach_loaf_validator(self, function):
        self._loaf_validator = function

    def attach_block_validator(self, function):
        self._block_validator = function

    def validate_loaf(self, loaf):
        return self._loaf_validator(loaf)

    def validate_block(self, block):
        return self._block_validator(block)
