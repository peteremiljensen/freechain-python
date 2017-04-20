#!/usr/bin/env python3

import datetime
import time
import sys
from cmd import Cmd

from blockchain.node import *
from blockchain.common import *

#                   _
#                  (_)
#   _ __ ___   __ _ _ _ __
#  | '_ ` _ \ / _` | | '_ \
#  | | | | | | (_| | | | | |
#  |_| |_| |_|\__,_|_|_| |_|
#
#

def loaf_validator(loaf):
    hash_calc = loaf.calculate_hash()
    return loaf.get_hash() == hash_calc

def block_validator(block):
    hash_calc = block.calculate_hash()
    return block.get_hash() == hash_calc and \
           hash_calc[:4] == '0000'

class Prompt(Cmd):
    PRINTS = ['loaf_pool', 'mined_loaves', 'blockchain', 'block_hash']

    def __init__(self):
        """ Prompt class constructor
        """
        super().__init__()
        self._node = Node(port)
        self._node.start()

        self._node.attach_loaf_validator(loaf_validator)
        self._node.attach_block_validator(block_validator)

    def do_connect(self, args):
        """ Parses the arguments to get nodes ip and connects to node
        """
        l = args.split()
        if len(l) > 2:
            print(fail("invalid number of arguments"))
            return
        try:
            ip = l[0]
            if len(l) == 2:
                self._node.connect_node(ip, l[1])
            else:
                self._node.connect_node(ip)
        except:
            print(fail("error connecting to node"))
            raise

    def do_mine(self, args):
        """ Reads argument and tries to mine block. if block is mined,
            the block is added to the chain and broadcasted
        """
        l = args.split()
        if len(l) != 0:
            print (fail("mine doesnt take any arguments"))
            return
        try:
            block = self._node.mine()
            if block is None:
                print(fail("failed to mine block"))
            else:
                if self._node.add_block(block):
                    self._node.broadcast_block(block)
                else:
                    print(fail("failed to add block"))
        except:
            print(fail("error trying to mine"))
            raise

    def do_loaf(self, args):
        """ Parses the argument to get loaf data, creates a loaf from data,
            adds loaf to loaf pool and broadcasts the loaf
        """
        l = args.split()
        if len(l) != 1:
            print(fail("invalid number of arguments"))
            return
        try:
            loaf = Loaf({"string": l[0]})
            if self._node.add_loaf(loaf):
                self._node.broadcast_loaf(loaf)
            else:
                print(fail("failed to add loaf to loaf pool"))
        except:
            print(fail("error creating and broadcasting loaf"))
            raise

    def do_loafbomb(self, args):
        """ Does as do_loaf, but does it a number of times, depending on the
            number given as the second argument
        """
        l = args.split()
        if len(l) != 2:
            print(fail("invalid number of arguments"))
            return
        try:
            for i in range(int(l[1])):
                loaf = Loaf({"string": l[0]+str(i)})
                if self._node.add_loaf(loaf):
                    self._node.broadcast_loaf(loaf)
                else:
                    print(fail("failed to add loaf to loaf pool"))
        except:
            print(fail("error creating and broadcasting loaf"))
            raise

    def do_print(self, args):
        """ Prints loaf pool or blockchain
        """
        l = args.split()
        try:
            if l[0] == self.PRINTS[0]:
                for loaf in list(self._node._loaf_pool.values()):
                    print(loaf.json())
            elif l[0] == self.PRINTS[1]:
                print(self._node._mined_loaves)
            elif l[0] == self.PRINTS[2]:
                print(self._node._chain.json())
            elif l[0] == self.PRINTS[3]:
                if len(l) != 2:
                    print(fail("invalid number of arguments"))
                else:
                    if self._node._chain.get_length() > int(l[1]):
                        print(self._node._chain.get_block(int(l[1])).get_hash())
                    else:
                        print(fail("Blockchain doesn't contain a block of height " + 
                              str(l[1])))
            else:
                print(fail(l[0] + " doesn't exist"))

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
        """ Calls do_quit if at end of file
        """
        self.do_quit(line)

    def do_quit(self, args):
        """ Quits program
        """
        print(info("Quitting"))
        raise SystemExit

    def do_q(self, args):
        self.do_quit(args)

    def emptyline(self):
        """ If empty line is sent, does nothing
        """
        return

if __name__ == '__main__':
    """ Program start. If no port argument is given, sets port to 9000.
        Prints error if more than one argument is given, then creates a prompt
        object and waits for user input
    """
    if len(sys.argv) == 1:
        port = 9000
    elif len(sys.argv) == 2:
        port = sys.argv[1]
    else:
        print(fail("you must supply 0 or 1 argument"))
        sys.exit()

    prompt = Prompt()
    prompt.prompt = '(freechain) '
    try:
        prompt.cmdloop(info('Starting node on port ' + str(port) + "..."))
    except KeyboardInterrupt:
        prompt.do_quit(None)
    except SystemExit:
        pass
    except:
        print(fail("fatal error"))
        raise
