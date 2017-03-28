#!/usr/bin/env python3

import datetime
import time
import sys
from cmd import Cmd

from blockchain.node import Node

class Prompt(Cmd):
    def __init__(self):
        super().__init__()
        self._node = Node(port)
        self._node.start()

    def do_connect(self, args):
        l = args.split()
        if len(l) != 1:
            print("*** invalid number of arguments")
            return
        try:
            ip = l[0]
            self._node.connect_node(ip)
        except:
            print("*** error connecting to node")
            raise

    def do_EOF(self, line):
        self.do_quit(line)

    def do_quit(self, args):
        print("Quitting")
        raise SystemExit

if __name__ == '__main__':
    if len(sys.argv) == 1:
        port = 9000
    elif len(sys.argv) == 2:
        port = sys.argv[1]
    else:
        print("*** you must supply 0 or 1 argument")
        sys.exit()

    prompt = Prompt()
    prompt.prompt = '> '
    try:
        prompt.cmdloop('Starting node...')
    except KeyboardInterrupt:
        prompt.do_quit(None)
