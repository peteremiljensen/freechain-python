#!/usr/bin/env python3

import datetime
import time

from blockchain.node import Node

def main():
    node = Node('9000')
    node.start()
    while True:
        time.sleep(1)

if __name__ == '__main__':
    main()
