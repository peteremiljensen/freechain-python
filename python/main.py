#!/usr/bin/env python3

import datetime
from blockchain.loaf import Loaf
from blockchain.block import Block

def main():
    data_1 = {"Which": "The first loaf"}
    data_2 = {"Which": "The second loaf"}
    loaf_1 = Loaf(data_1)
    loaf_2 = Loaf(data_2)
    timestamp = str(datetime.datetime.now())
    previous_block = "0"
    loafs = [loaf_1, loaf_2]
    nounce = 0
    block = None
    while True:
        block = Block(loafs, previous_block, timestamp, nounce)
        if block.get_hash()[:4] == '0000':
            print (block.json())
            break
        nounce += 1

    print(block.validate())

if __name__ == '__main__':
    main()
