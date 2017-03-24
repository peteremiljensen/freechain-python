#!/usr/bin/env python3

import datetime
import time

from blockchain.node import Node

def main():
    node = Node('9000')
    node.start()
    ip = input('Connect to: ')
    node.connect_node(ip)
    while True:
        data = input('Send data: ')
        node.broadcast(data)

if __name__ == '__main__':
    main()
