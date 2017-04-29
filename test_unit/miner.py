import datetime
from ..block import Block

def mine(loaves, prev_block):
    height = prev_block.get_height() + 1
    previous_block_hash = prev_block.get_hash()
    timestamp = str(datetime.datetime.now())
    nounce = 0
    block = None
    while True:
        block = Block(loaves, height, previous_block_hash, timestamp, nounce)
        if block.get_hash()[:4] == '0000':
            return block
        nounce += 1

    if block.validate():
        return block
    else:
        print(fail('block could not be mined'))
        return None
