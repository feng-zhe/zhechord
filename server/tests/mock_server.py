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
        node_id = url[7:pos]
        pos = url.rfind('/')
        path = url[pos:]
        # dispatch
        rsp = MockResponse(200, {})
        if path == '/find_predecessor':
            pred = self._nodes[node_id].find_predecessor(json['id'])
            rsp = MockResponse(200, {'id': pred})
        elif path == '/set_predecessor':
            self._nodes[node_id].set_predecessor(json['id'])
        elif path == '/find_successor':
            succ = self._nodes[node_id].find_successor(json['id'])
            rsp = MockResponse(200, {'id': succ})
        elif path == '/closest_preceding_finger':
            cpf = self._nodes[node_id].closest_preceding_finger(json['id'])
            rsp = MockResponse(200, {'id': cpf})
        elif path == '/update_finger_table':
            self._nodes[node_id].update_finger_table(json['s'], json['i'])
        else:
            rsp = MockResponse(400, {})

        return rsp

class MockResponse(object):
    
    def __init__(self, status_code, json_dict):
        self.status_code = status_code
        self._json_dict = json_dict

    def json(self):
        return self._json_dict

