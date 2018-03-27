'''
Shared values among files.
'''
import threading
import time
import mychord.node as node

# shared values
g_node = None

def period():
    '''
    Periodically call the stabilize and fix_finger_table
    '''
    while True:
        g_node.stabilize()
        g_node.fix_fingers(True)        # TODO: change to random after docker test is passed
        time.sleep(1)

def init(self_id, remote_id=None):
    global g_node 
    g_node = node.Node(self_id)
    g_node.join(remote_id)
    t = threading.Thread(target=period)
    t.daemon = True
    t.start()
