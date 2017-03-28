#!/usr/bin/env python3

import datetime
import time
import sys
from cmd import Cmd

from blockchain.node import *

class Prompt(Cmd):
    PRINTS = ['loaf_pool']

    def __init__(self):
        super().__init__()
        self._node = Node(port)
        self._node.start()

    def do_connect(self, args):
        l = args.split()
        if len(l) != 1:
            print(fail("invalid number of arguments"))
            return
        try:
            ip = l[0]
            self._node.connect_node(ip)
        except:
            print(fail("error connecting to node"))
            raise

    def do_loaf(self, args):
        l = args.split()
        if len(l) != 1:
            print(fail("invalid number of arguments"))
            return
        try:
            loaf = Loaf({"string": l[0]})
            self._node.broadcast_loaf(loaf)
        except:
            print(fail("error creating and broadcasting loaf"))
            raise

    def do_print(self, args):
        l = args.split()
        if len(l) != 1:
            print(fail("invalid number of arguments"))
            return
        try:
            if l[0] == self.PRINTS[0]:
                for loaf in list(self._node._loaf_pool.values()):
                    print(loaf.json())
        except:
            print(fail("error printing"))
            raise

    def complete_print(self, text, line, begidx, endidx):
        if not text:
            completions = self.PRINTS[:]
        else:
            completions = [f for f in self.PRINTS
                            if f.startswith(text)]
        return completions

    def do_EOF(self, line):
        self.do_quit(line)

    def do_quit(self, args):
        print("Quitting")
        raise SystemExit

    def emptyline(self):
        return

if __name__ == '__main__':
    if len(sys.argv) == 1:
        port = 9000
    elif len(sys.argv) == 2:
        port = sys.argv[1]
    else:
        print(fail("you must supply 0 or 1 argument"))
        sys.exit()

    prompt = Prompt()
    prompt.prompt = '> '
    try:
        prompt.cmdloop(info('Starting node on port ' + str(port) + "..."))
    except KeyboardInterrupt:
        prompt.do_quit(None)
    except SystemExit:
        pass
    except:
        print(fail("fatal error"))
        raise
