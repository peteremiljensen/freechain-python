
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
    RECEIVED_LOAF = 'received_loaf'
    RECEIVED_BLOCK = 'received_block'

class FUNCTIONS:
    GET_LENGTH = 'get_length'
    GET_HASH = 'get_hash'
    GET_BLOCKS = 'get_blocks'
    BROADCAST_LOAF = 'broadcast_loaf'
    BROADCAST_BLOCK = 'broadcast_block'
