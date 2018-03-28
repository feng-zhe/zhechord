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
            self._response(200, { 'id': pred })
        elif path == '/get_predecessor':
            pred = sv.g_node.get_predecessor()
            self._response(200, { 'id': pred})
        elif path == '/set_predecessor':
            sv.g_node.set_predecessor(data['id'])
            self._response(200, {})
        elif path == '/find_successor':
            succ = sv.g_node.find_successor(data['id'])
            self._response(200, { 'id': succ })
        elif path == '/get_successor':
            succ = sv.g_node.get_successor()
            self._response(200, { 'id': succ})
        elif path == '/set_successor':
            sv.g_node.set_successor(data['id'])
            self._response(200, {})
        elif path == '/closest_preceding_finger':
            cpf = sv.g_node.closest_preceding_finger(data['id'])
            self._response(200, { 'id': cpf })
        elif path == '/notify':
            sv.g_node.notify(data['id'])
            self._response(200, {})
        elif path == '/display_finger_table':
            ft = sv.g_node.display_finger_table()
            self._response(200, { 'result': ft})
        elif path == '/put':
            sv.g_node.put(data['key'], data['value'])
            self._response(200, {})
        elif path == '/get':
            value = sv.g_node.get(data['key'])
            self._response(200, {'value': value})
        elif path == '/display_data':
            kv = sv.g_node.display_data()
            self._response(200, { 'result': kv})
        else:
            self._response(400, {})

    def _response(self, code, data):
        self.send_response(code)
        self.send_header('content-type', 'application/json')
        self.end_headers()
        self.wfile.write(json.dumps(data).encode('utf-8'))
