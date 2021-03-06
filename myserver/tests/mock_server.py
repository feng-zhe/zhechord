class MockServer(object):
    
    def __init__(self):
        self._nodes = {}        # the mapping for nodes

    def add_node(self, identity, node):
        self._nodes[identity] = node

    def post(self, url, json):
        '''
        Mock the post function.

        Args:
            url:    A string like 'http://node_id:8000/xxxx'.
            json:   A dict. The input json data.

        Returns:
            Return results according to corresponding functions.

        Raises:
            Raises exceptions/errors according to corresponding functions.
        '''
        # parse url
        pos = url.find(':', 5)
        node_id = url[10:pos]
        pos = url.rfind('/')
        path = url[pos:]
        # dispatch
        rsp = MockResponse(200, {})
        if path == '/find_predecessor':
            pred = self._nodes[node_id].find_predecessor(json['id'])
            rsp = MockResponse(200, {'id': pred})
        elif path == '/get_predecessor':
            pred = self._nodes[node_id].get_predecessor()
            rsp = MockResponse(200, {'id': pred})
        elif path == '/set_predecessor':
            self._nodes[node_id].set_predecessor(json['id'])
        elif path == '/find_successor':
            succ = self._nodes[node_id].find_successor(json['id'])
            rsp = MockResponse(200, {'id': succ})
        elif path == '/get_successor':
            succ = self._nodes[node_id].get_successor()
            rsp = MockResponse(200, {'id': succ})
        elif path == '/set_successor':
            self._nodes[node_id].set_successor(json['id'])
        elif path == '/closest_preceding_finger':
            cpf = self._nodes[node_id].closest_preceding_finger(json['id'])
            rsp = MockResponse(200, {'id': cpf})
        elif path == '/notify':
            self._nodes[node_id].notify(json['id'])
            rsp = MockResponse(200, {})
        elif path == '/display_finger_table':
            ft = self._nodes[node_id].display_finger_table()
            rsp = MockResponse(200, {'result': ft})
        elif path == '/put':
            self._nodes[node_id].put(json['key'], json['value'])
            rsp = MockResponse(200, {})
        elif path == '/get':
            value = self._nodes[node_id].get(json['key'])
            rsp = MockResponse(200, {'value': value})
        elif path == '/display_data':
            data = self._nodes[node_id].display_data()
            rsp = MockResponse(200, {'result': data})
        else:
            rsp = MockResponse(400, {})

        return rsp

    def period(self):
        '''
        Imitate the periodic operations on each node.

        Args:
            N/A

        Returns:
            N/A

        Raises:
            N/A
        '''
        for node in self._nodes.values():
            node.stabilize()
            node.fix_fingers(True)      # use loop for testing purpose

class MockResponse(object):
    
    def __init__(self, status_code, json_dict):
        self.status_code = status_code
        self._json_dict = json_dict

    def json(self):
        return self._json_dict

