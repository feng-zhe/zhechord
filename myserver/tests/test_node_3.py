'''
This file tests the core functionality of Node on a ring of 2^5=32 nodes.
'''
import unittest
import logging
from unittest.mock import patch
import myserver.mychord.constants as ct
from myserver.mychord.node import Node
from . import mock_server

MockServer = mock_server.MockServer

logging.basicConfig(level=logging.DEBUG)

logger = logging.getLogger(__name__)

class TestNodeCore(unittest.TestCase):
    '''
    Test class for Node.py
    '''

    _default_size = 0

    @classmethod
    def setUpClass(cls):
        '''
        Change to smaller ring.
        '''
        cls._default_size = ct.RING_SIZE_BIT
        ct.RING_SIZE_BIT = 5
        ct.init()

    @classmethod
    def tearDownClass(cls):
        '''
        Restore longer ring.
        '''
        ct.RING_SIZE_BIT = cls._default_size
        ct.init()

    @patch('requests.post')
    def test_join_0_1_3_11_15_1c(self, post_mock):
        '''
        Demo example for 32-node ring.
        Only test the final result.
        '''
        # set up mock server
        ms = MockServer()
        post_mock.side_effect = lambda url, json, timeout : ms.post(url, json)
        # node 0
        node_00 = Node('00')
        ms.add_node(node_00._id, node_00)       # add this node to mocked server
        node_00.join()
        # node 1
        node_01 = Node('01')
        ms.add_node(node_01._id, node_01)
        node_01.join(node_00._id)
        # node 3
        node_03 = Node('03')
        ms.add_node(node_03._id, node_03)
        node_03.join(node_01._id)
        # node 11 (17 in decimal)
        node_11 = Node('11')
        ms.add_node(node_11._id, node_11)
        node_11.join(node_03._id)
        # node 15 (21 in decimal)
        node_15 = Node('15')
        ms.add_node(node_15._id, node_15)
        node_15.join(node_11._id)
        # node 1c (29 in decimal)
        node_1c = Node('1c')
        ms.add_node(node_1c._id, node_1c)
        node_1c.join(node_15._id)
        # imitate the periodic operations
        for i in range(0, 10):
            ms.period()
        # test values
        self.assertEqual(node_00.get_predecessor(), node_1c._id) # node 0 status
        self.assertEqual(node_00._table.get_node(1), node_01._id)
        self.assertEqual(node_00._table.get_node(2), node_03._id)
        self.assertEqual(node_00._table.get_node(3), node_11._id)
        self.assertEqual(node_00._table.get_node(4), node_11._id)
        self.assertEqual(node_00._table.get_node(5), node_11._id)
        self.assertEqual(node_01.get_predecessor(), node_00._id) # node 1 status
        self.assertEqual(node_01._table.get_node(1), node_03._id)
        self.assertEqual(node_01._table.get_node(2), node_03._id)
        self.assertEqual(node_01._table.get_node(3), node_11._id)
        self.assertEqual(node_01._table.get_node(4), node_11._id)
        self.assertEqual(node_01._table.get_node(5), node_11._id)
        self.assertEqual(node_03.get_predecessor(), node_01._id) # node 3 status
        self.assertEqual(node_03._table.get_node(1), node_11._id)
        self.assertEqual(node_03._table.get_node(2), node_11._id)
        self.assertEqual(node_03._table.get_node(3), node_11._id)
        self.assertEqual(node_03._table.get_node(4), node_11._id)
        self.assertEqual(node_03._table.get_node(5), node_15._id)
        self.assertEqual(node_11.get_predecessor(), node_03._id) # node 11 status
        self.assertEqual(node_11._table.get_node(1), node_15._id)
        self.assertEqual(node_11._table.get_node(2), node_15._id)
        self.assertEqual(node_11._table.get_node(3), node_15._id)
        self.assertEqual(node_11._table.get_node(4), node_1c._id)
        self.assertEqual(node_11._table.get_node(5), node_01._id)
        self.assertEqual(node_15.get_predecessor(), node_11._id) # node 15 status
        self.assertEqual(node_15._table.get_node(1), node_1c._id)
        self.assertEqual(node_15._table.get_node(2), node_1c._id)
        self.assertEqual(node_15._table.get_node(3), node_1c._id)
        self.assertEqual(node_15._table.get_node(4), node_00._id)
        self.assertEqual(node_15._table.get_node(5), node_11._id)
        self.assertEqual(node_1c.get_predecessor(), node_15._id) # node 1c status
        self.assertEqual(node_1c._table.get_node(1), node_00._id)
        self.assertEqual(node_1c._table.get_node(2), node_00._id)
        self.assertEqual(node_1c._table.get_node(3), node_00._id)
        self.assertEqual(node_1c._table.get_node(4), node_11._id)
        self.assertEqual(node_1c._table.get_node(5), node_11._id)

if __name__ == '__main__':
    unittest.main()
