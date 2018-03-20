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
            pred = sv.g_node.find_predecessor(data['id'])
            _response(200, { 'id': pred })
        elif path == '/get_predecessor':
            pred = sv.g_node.get_predecessor()
            _response(200, { 'id': pred})
        elif path == '/set_predecessor':
            sv.g_node.set_predecessor(data['id'])
            _response(200, {})
        elif path == '/find_successor':
            succ = sv.g_node.find_successor(data['id'])
            _response(200, { 'id': succ })
        elif path == '/get_successor':
            succ = sv.g_node.get_successor()
            _response(200, { 'id': succ})
        elif path == '/closet_preceding_finger':
            cpf = sv.g_node.closet_preceding_finger(data['id'])
            _response(200, { 'id': cpf })
        elif path == '/update_finger_table':
            sv.g_node.update_finger_table(data['s'], data['i'])
            _response(200, {})
        else:
            _response(400, {})

    def _response(self, code, data):
        self.send_response(code)
        self.send_header('content-type', 'application/json')
        self.end_headers()
        self.wfile.write(json.dumps(data).encode('utf-8'))
