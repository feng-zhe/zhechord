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

    _default_size = 0

    @classmethod
    def setUpClass(cls):
        '''
        Change to smaller ring.
        '''
        cls._default_size = ct.RING_SIZE_BIT
        ct.RING_SIZE_BIT = 3
        ct.init()

    @classmethod
    def tearDownClass(cls):
        '''
        Restore longer ring.
        '''
        ct.RING_SIZE_BIT = cls._default_size
        ct.init()

    @patch('requests.post')
    def test_join_0_3_1_6(self, post_mock):
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
        for i in range(0, 10):      # imitate the periodic operations
            ms.period()
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
        for i in range(0, 10):      # imitate the periodic operations
            ms.period()
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
        for i in range(0, 10):      # imitate the periodic operations
            ms.period()
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

    @patch('requests.post')
    def test_join_6_1_3_0(self, post_mock):
        '''
        Use the example in paper.
        '''
        # set up mock server
        ms = MockServer()
        post_mock.side_effect = lambda url, json : ms.post(url, json)
        # test 1: node 6 creates a new ring
        node_6 = Node('6')
        ms.add_node(node_6._id, node_6)       # add this node to mocked server
        node_6.join()
        for i in range(1, ct.RING_SIZE_BIT+1):      # should point to itself
            self.assertEqual(
                    node_6._table.get_node(i), 
                    node_6._id)
        # test 2: join node 1 to then ring
        node_1 = Node('1')
        ms.add_node(node_1._id, node_1)
        node_1.join(node_6._id)
        for i in range(0, 10):      # imitate the periodic operations
            ms.period()
        self.assertEqual(node_1._table.get_node(1), node_6._id) # node 1 status
        self.assertEqual(node_1._table.get_node(2), node_6._id)
        self.assertEqual(node_1._table.get_node(3), node_6._id)
        self.assertEqual(node_1.get_predecessor(), node_6._id)
        self.assertEqual(node_6._table.get_node(1), node_1._id) # node 6 status
        self.assertEqual(node_6._table.get_node(2), node_1._id)
        self.assertEqual(node_6._table.get_node(3), node_6._id)
        self.assertEqual(node_6.get_predecessor(), node_1._id)
        # test 3: join node 3 to the ring
        node_3 = Node('3')
        ms.add_node(node_3._id, node_3)
        node_3.join(node_1._id)
        for i in range(0, 10):      # imitate the periodic operations
            ms.period()
        self.assertEqual(node_3._table.get_node(1), node_6._id) # node 3 status
        self.assertEqual(node_3._table.get_node(2), node_6._id)
        self.assertEqual(node_3._table.get_node(3), node_1._id)
        self.assertEqual(node_3.get_predecessor(), node_1._id)
        self.assertEqual(node_1._table.get_node(1), node_3._id) # node 1 status
        self.assertEqual(node_1._table.get_node(2), node_3._id)
        self.assertEqual(node_1._table.get_node(3), node_6._id)
        self.assertEqual(node_1.get_predecessor(), node_6._id)
        self.assertEqual(node_6._table.get_node(1), node_1._id) # node 6 status
        self.assertEqual(node_6._table.get_node(2), node_1._id)
        self.assertEqual(node_6._table.get_node(3), node_3._id)
        self.assertEqual(node_6.get_predecessor(), node_3._id)
        # test 4: join node 0 to the ring
        node_0 = Node('0')
        ms.add_node(node_0._id, node_0)
        node_0.join(node_3._id)
        for i in range(0, 10):      # imitate the periodic operations
            ms.period()
        self.assertEqual(node_0._table.get_node(1), node_1._id) # node 0 status
        self.assertEqual(node_0._table.get_node(2), node_3._id)
        self.assertEqual(node_0._table.get_node(3), node_6._id)
        self.assertEqual(node_0.get_predecessor(), node_6._id)
        self.assertEqual(node_3._table.get_node(1), node_6._id) # node 3 status
        self.assertEqual(node_3._table.get_node(2), node_6._id)
        self.assertEqual(node_3._table.get_node(3), node_0._id)
        self.assertEqual(node_3.get_predecessor(), node_1._id)
        self.assertEqual(node_1._table.get_node(1), node_3._id) # node 1 status
        self.assertEqual(node_1._table.get_node(2), node_3._id)
        self.assertEqual(node_1._table.get_node(3), node_6._id)
        self.assertEqual(node_1.get_predecessor(), node_0._id)
        self.assertEqual(node_6._table.get_node(1), node_0._id) # node 6 status
        self.assertEqual(node_6._table.get_node(2), node_0._id)
        self.assertEqual(node_6._table.get_node(3), node_3._id)
        self.assertEqual(node_6.get_predecessor(), node_3._id)

    @patch('requests.post')
    def test_display_finger_table(self, post_mock):
        # set up mock server
        ms = MockServer()
        post_mock.side_effect = lambda url, json : ms.post(url, json)
        # test:  join 3 node
        logging.disable(logging.DEBUG)      # disable logging
        node_0 = Node('0')
        ms.add_node(node_0._id, node_0)
        node_0.join()
        node_3 = Node('3')
        ms.add_node(node_3._id, node_3)
        node_3.join(node_0._id)
        for i in range(0, 10):
            ms.period()
        node_1 = Node('1')
        ms.add_node(node_1._id, node_1)
        node_1.join(node_3._id)
        for i in range(0, 10):
            ms.period()
        logging.disable(logging.NOTSET)      # enable logging
        ft = node_0.display_finger_table()
        self.assertEqual(ft[0], '3')
        self.assertEqual(ft[1], '1')
        self.assertEqual(ft[2], '3')
        self.assertEqual(ft[3], '0')
        ft = node_3.display_finger_table()
        self.assertEqual(ft[0], '1')
        self.assertEqual(ft[1], '0')
        self.assertEqual(ft[2], '0')
        self.assertEqual(ft[3], '0')
        ft = node_1.display_finger_table()
        self.assertEqual(ft[0], '0')
        self.assertEqual(ft[1], '3')
        self.assertEqual(ft[2], '3')
        self.assertEqual(ft[3], '0')

    @patch('requests.post')
    def test_put_get(self, post_mock):
        # set up mock server
        ms = MockServer()
        post_mock.side_effect = lambda url, json : ms.post(url, json)
        # create nodes
        logging.disable(logging.DEBUG)      # disable logging
        node_0 = Node('0')
        ms.add_node(node_0._id, node_0)
        node_0.join()
        node_3 = Node('3')
        ms.add_node(node_3._id, node_3)
        node_3.join(node_0._id)
        for i in range(0, 10):
            ms.period()
        node_1 = Node('1')
        ms.add_node(node_1._id, node_1)
        node_1.join(node_3._id)
        for i in range(0, 10):
            ms.period()
        logging.disable(logging.NOTSET)      # enable logging
        # put&get key-value
        node_0.put('hello', 'world')
        self.assertEqual(node_0.get('hello'), 'world')
        self.assertEqual(node_3.get('hello'), 'world')
        self.assertEqual(node_1.get('hello'), 'world')

if __name__ == '__main__':
    unittest.main()
