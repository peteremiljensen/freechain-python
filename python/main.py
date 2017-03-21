#!/usr/bin/env python3

import datetime
from blockchain.chain import Chain
from blockchain.loaf import Loaf
from blockchain.block import Block

def main():
    chain = Chain()
    new_block = chain.mine_block([Loaf({"Which": 0}), Loaf({"Which": 1})])
    if chain.add_block(new_block):
        print (chain.json())
    else:
        print ("Error adding block")

if __name__ == '__main__':
    main()
