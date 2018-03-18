'''
Main file for running a node server
'''
import sys
from http.server import HTTPServer
import handler as handler
import node
import shared_values as sv

def run(server_class=HTTPServer, handler_class=handler.ChordServerHandler):
    server_address = ('', 8000)
    httpd = server_class(server_address, handler_class)
    httpd.serve_forever()

if __name__ == '__main__':
    if len(sys.argv)<=1:
        print('Usage: server.py SELF_ID [JOIN_NODE_ID]')
    else:
        # init node
        sv.g_node = node.Node(sys.argv[1])
        sv.g_node.join(sys.argv[2] if len(sys.argv)==3 else None)
        # listen to requests
        run()
