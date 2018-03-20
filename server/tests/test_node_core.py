'''
This file tests the core functionality of Node on small rings.
'''
import unittest
import logging
from unittest.mock import patch
import mychord.constants as ct
from mychord.node import Node
from tests.mock_server import MockServer

logging.basicConfig(level=logging.DEBUG)

logger = logging.getLogger(__name__)

class TestNodeCore(unittest.TestCase):
    '''
    Test class for Node.py
    '''
    @classmethod
    def setUpClass(cls):
        '''
        Change to smaller ring.
        '''
        ct.RING_SIZE_BIT = 3
        ct.init()

    @classmethod
    def tearDownClass(cls):
        '''
        Restore longer ring.
        '''
        ct.RING_SIZE_BIT = 160
        ct.init()

    @patch('requests.post')
    def test_join(self, post_mock):
        '''
        Use the example in paper.
        '''
        # set up mock server
        ms = MockServer()
        post_mock.side_effect = lambda url, json : ms.post(url, json)
        # test 1: node 0 creates a new ring
        node_0 = Node('0')
        ms.add_node(node_0._id, node_0)       # add this node to mocked server
        node_0.join()
        for i in range(1, ct.RING_SIZE_BIT+1):      # should point to itself
            self.assertEqual(
                    node_0._table.get_node(i), 
                    node_0._id)
        # test 2: join node 3 to then ring
        node_3 = Node('3')
        ms.add_node(node_3._id, node_3)
        node_3.join(node_0._id)
        self.assertEqual(node_3._table.get_node(1), node_0._id) # node 3 status
        self.assertEqual(node_3._table.get_node(2), node_0._id)
        self.assertEqual(node_3._table.get_node(3), node_0._id)
        self.assertEqual(node_3.get_predecessor(), node_0._id)
        self.assertEqual(node_0._table.get_node(1), node_3._id) # node 0 status
        self.assertEqual(node_0._table.get_node(2), node_3._id)
        self.assertEqual(node_0._table.get_node(3), node_0._id)
        self.assertEqual(node_0.get_predecessor(), node_3._id)
        # test 3: join node 1 to the ring
        node_1 = Node('1')
        ms.add_node(node_1._id, node_1)
        node_1.join(node_3._id)
        self.assertEqual(node_1._table.get_node(1), node_3._id) # node 1 status
        self.assertEqual(node_1._table.get_node(2), node_3._id)
        self.assertEqual(node_1._table.get_node(3), node_0._id)
        self.assertEqual(node_1.get_predecessor(), node_0._id)
        self.assertEqual(node_3._table.get_node(1), node_0._id) # node 3 status
        self.assertEqual(node_3._table.get_node(2), node_0._id)
        self.assertEqual(node_3._table.get_node(3), node_0._id)
        self.assertEqual(node_3.get_predecessor(), node_1._id)
        self.assertEqual(node_0._table.get_node(1), node_1._id) # node 0 status
        self.assertEqual(node_0._table.get_node(2), node_3._id)
        self.assertEqual(node_0._table.get_node(3), node_0._id)
        self.assertEqual(node_0.get_predecessor(), node_3._id)
        # test 4: join node 6 to the ring
        node_6 = Node('6')
        ms.add_node(node_6._id, node_6)
        node_6.join(node_1._id)
        self.assertEqual(node_6._table.get_node(1), node_0._id) # node 6 status
        self.assertEqual(node_6._table.get_node(2), node_0._id)
        self.assertEqual(node_6._table.get_node(3), node_3._id)
        self.assertEqual(node_6.get_predecessor(), node_3._id)
        self.assertEqual(node_1._table.get_node(1), node_3._id) # node 1 status
        self.assertEqual(node_1._table.get_node(2), node_3._id)
        self.assertEqual(node_1._table.get_node(3), node_6._id)
        self.assertEqual(node_1.get_predecessor(), node_0._id)
        self.assertEqual(node_3._table.get_node(1), node_6._id) # node 3 status
        self.assertEqual(node_3._table.get_node(2), node_6._id)
        self.assertEqual(node_3._table.get_node(3), node_0._id)
        self.assertEqual(node_3.get_predecessor(), node_1._id)
        self.assertEqual(node_0._table.get_node(1), node_1._id) # node 0 status
        self.assertEqual(node_0._table.get_node(2), node_3._id)
        self.assertEqual(node_0._table.get_node(3), node_6._id)
        self.assertEqual(node_0.get_predecessor(), node_6._id)

if __name__ == '__main__':
    unittest.main()
