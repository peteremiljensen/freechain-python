#!/usr/bin/env python3

import datetime
import time
import sys

from blockchain.node import Node

if len(sys.argv) == 1:
    port = 9000
elif len(sys.argv) == 2:
    port = sys.argv[1]
else:
    print("You must supply 0 or 1 argument")
    sys.exit()

def main():
    node = Node(port)
    node.start()
    while True:
        inp = input().split()
        if inp[0] == "connect":
            if len(inp) == 2:
                ip = inp[1]
                node.connect_node(ip)
                print("Connected to:", ip)
            else:
                print("Invalid input")
        elif inp[0] == "length":
            node.get_length()
        else:
            print("Unknown command:", inp[0])

if __name__ == '__main__':
    main()
