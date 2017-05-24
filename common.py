import sys, os

#    ___ ___  _ __ ___  _ __ ___   ___  _ __
#   / __/ _ \| '_ ` _ \| '_ ` _ \ / _ \| '_ \
#  | (_| (_) | | | | | | | | | | | (_) | | | |
#   \___\___/|_| |_| |_|_| |_| |_|\___/|_| |_|
#

def info(string):
    return('\033[92m' + string + '\033[0m')
def warning(string):
    return('\033[93m*** ' + string + '\033[0m')
def fail(string):
    return('\033[91m*** ' + string + '\033[0m')

class EVENTS_TYPE:
    NEW_CLIENT_CONNECTION = 'new_client_connection'
    CONNECTION_READY = 'connection_ready'
    CONNECTION_CLOSED = 'connection_closed'
    RECEIVED_LOAF = 'received_loaf'
    RECEIVED_BLOCK = 'received_block'
    BLOCKS_ADDED = 'blocks_added'
    RECEIVED_ERROR = 'received_error'

class FUNCTIONS:
    GET_HASHES = 'get_hashes'
    GET_BLOCKS = 'get_blocks'
    BROADCAST_LOAF = 'broadcast_loaf'
    BROADCAST_BLOCK = 'broadcast_block'
