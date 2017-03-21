#!/usr/bin/env python3

import datetime
from blockchain.chain import Chain
from blockchain.loaf import Loaf
from blockchain.block import Block

def main():
    chain = Chain()
    for i in range(5):
        new_block = chain.mine_block([Loaf({"Which": 0}), Loaf({"Which": 1})])
        if chain.add_block(new_block):
            print ("Added block")
        else:
            print ("Error adding block")
    print (chain.json())

if __name__ == '__main__':
    main()
