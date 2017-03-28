#!/usr/bin/env python3

import datetime
import time
import sys
from cmd import Cmd

from blockchain.node import Node

def info(string):
    return('\033[92m' + string + '\033[0m')

def warning(string):
    return('\033[93m' + string + '\033[0m')

def fail(string):
    return('\033[91m' + string + '\033[0m')

class Prompt(Cmd):
    def __init__(self):
        super().__init__()
        self._node = Node(port)
        self._node.start()

    def do_connect(self, args):
        l = args.split()
        if len(l) != 1:
            print(fail("*** invalid number of arguments"))
            return
        try:
            ip = l[0]
            self._node.connect_node(ip)
        except:
            print(fail("*** error connecting to node"))
            raise

#    def do_loaf(self, args):

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
        print(fail("*** you must supply 0 or 1 argument"))
        sys.exit()

    prompt = Prompt()
    prompt.prompt = '> '
    try:
        prompt.cmdloop(info('Starting node...'))
    except KeyboardInterrupt:
        prompt.do_quit(None)
