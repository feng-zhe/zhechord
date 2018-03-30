'''
Shared values among files.
'''
import random
import threading
import time
from . import node

# shared values
g_node = None

def period():
    '''
    Periodically call the stabilize and fix_finger_table
    '''
    while True:
        g_node.stabilize()
        g_node.fix_fingers(True)        # TODO: change to random after docker test is passed
        rand_t = random.randint(50, 100) / 10
        time.sleep(rand_t)

def init(self_id, remote_id=None):
    global g_node 
    g_node = node.Node(self_id)
    g_node.join(remote_id)
    t = threading.Thread(target=period)
    t.daemon = True
    t.start()
