from http.server import BaseHTTPRequestHandler
import shared_values as sv

class ChordServerHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        self.send_response(200, 'done')
        self.send_header('content-type', 'application/json')
        self.end_headers()
        self.wfile.write(b'{}')

    def do_POST(self):
        self.send_response(200, 'done')
        self.send_header('content-type', 'application/json')
        self.end_headers()
        self.wfile.write(b'{}')
