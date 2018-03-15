'''
Main file for running a node server
'''
from http.server import HTTPServer
import handler

def run(server_class=HTTPServer, handler_class=handler.ChordServerHandler):
    server_address = ('', 8000)
    httpd = server_class(server_address, handler_class)
    httpd.serve_forever()

if __name__ == '__main__':
    run()
