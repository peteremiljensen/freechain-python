#!/usr/bin/env python3

import datetime
import time

from blockchain.node import Node

def main():
    node = Node('9000')
    node.start()
    while True:
        inp = input().split()
        if inp[0] == "connect":
            if len(inp) == 2:
                ip = inp[1]
                node.connect_node(ip)
            else:
                print("Invalid input")
        elif inp[0] == "length":
            node.get_length()
        else:
            print("Unknown command:", inp[0])

if __name__ == '__main__':
    main()
