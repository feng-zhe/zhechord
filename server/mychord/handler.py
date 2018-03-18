import json
from http.server import BaseHTTPRequestHandler
import mychord.shared_values as sv

class ChordServerHandler(BaseHTTPRequestHandler):

    def do_POST(self):
        # parse request
        ct_len = int(self.headers['Content-Length'])
        data = json.loads(self.rfile.read(ct_len).decode('utf-8'))
        path = self.path
        # dispatch requests
        if path == '/find_predecessor':
            pass
        elif path == '/set_predecessor':
            pass
        elif path == '/find_successor':
            pass
        elif path == '/closet_preceding_finger':
            pass
        elif path == '/update_finger_table':
            pass
        else:
            pass

    def _response(self, code, data):
        self.send_response(code)
        self.send_header('content-type', 'application/json')
        self.end_headers()
        self.wfile.write(json.dumps(data).encode('utf-8'))
