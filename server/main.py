'''
Main file for running a node server
'''
import sys
import logging
from http.server import HTTPServer
import mychord.handler as handler
import mychord.shared_values as sv

logging.basicConfig(level=logging.INFO)

def run(server_class=HTTPServer, handler_class=handler.ChordServerHandler):
    server_address = ('', 8000)
    httpd = server_class(server_address, handler_class)
    httpd.serve_forever()

if __name__ == '__main__':
    if len(sys.argv)<=1:
        print('Usage: server.py SELF_ID [JOIN_NODE_ID]')
    else:
        print('self id is: {}'.format(sys.argv[1]))
        # init node
        if len(sys.argv)==2:
            sv.init(sys.argv[1])
        else:
            print('join the ring via: node {}'.format(sys.argv[2]))
            sv.init(sys.argv[1], sys.argv[2])
        # listen to requests
        print('Start listening...')
        run()
