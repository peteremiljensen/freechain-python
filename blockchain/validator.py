from blockchain.singleton import Singleton

@Singleton
class Validator():
    def __init__(self):
        self._loaf_validator  = lambda l: return True
        self._block_validator = lambda b: return True

    def attach_loaf_validator(function):
        self._loaf_validator = function

    def attach_block_validator(function):
        self._block_validator = function

    def validate_loaf(loaf):
        self._loaf_validator(loaf)

    def validate_block(block):
        self._block_validator(block)
