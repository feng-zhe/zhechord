'''
Shared values among files.
'''
import mychord.node as node

# shared values
g_node = None

def init(self_id, remote_id=None):
    g_node = node.Node(self_id)
    g_node.join(remote_id)
