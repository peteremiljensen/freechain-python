import datetime
from .. import block

def miner(loaves, height, previous_block_hash):
    b = None
    timestamp = str(datetime.datetime.now())
    nounce = 0
    while True:
        b = block.Block(loaves, height, previous_block_hash, timestamp, nounce)
        if b.get_hash()[:4] == '0000':
            break
        nounce += 1
    return b
