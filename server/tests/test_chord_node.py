import unittest
import logging
from unittest.mock import patch
import mychord.constants as ct
from mychord.node import Node
from tests.mock_server import MockServer

logging.basicConfig(level=logging.DEBUG)

logger = logging.getLogger(__name__)

class TestChordNode(unittest.TestCase):
    '''
    Test class for Node.py
    '''
    def test_in_range_ie(self):
        '''
        test the [start, end)
        '''
        h = 'b444ac06613fc8d63795be9ad0beaf55011936ac'
        node = Node(h)
        # start==end
        test = h
        start = h
        end = h
        self.assertFalse(node._in_range_ie(test, start, end))
        # start<h<end
        test = h
        start = format(int(h, 16) - 10, 'x')
        end = format(int(h, 16) + 10, 'x')
        self.assertTrue(node._in_range_ie(test, start, end))
        # start=h<end
        test = h
        start = h
        end = format(int(h, 16) + 10, 'x')
        self.assertTrue(node._in_range_ie(test, start, end))
        # start<h<=end
        test = h
        start = format(int(h, 16) - 10, 'x')
        end = h
        self.assertFalse(node._in_range_ie(test, start, end))
        # h<start<end
        test = h
        start = format(int(h, 16) + 10, 'x')
        end = format(int(h, 16) + 20, 'x')
        self.assertFalse(node._in_range_ie(test, start, end))
        # start>end, h is in
        test = format(1, '040x')
        start = h
        end = format(int(h, 16)//2, 'x')
        self.assertTrue(node._in_range_ie(test, start, end))

    def test_in_range_ei(self):
        '''
        test the (start, end]
        '''
        h = 'b444ac06613fc8d63795be9ad0beaf55011936ac'
        node = Node(h)
        # start==end
        test = h
        start = h
        end = h
        self.assertFalse(node._in_range_ei(test, start, end))
        # start<test<end
        test = h
        start = format(int(h, 16) - 10, 'x')
        end = format(int(h, 16) + 10, 'x')
        self.assertTrue(node._in_range_ei(test, start, end))
        # start=h<end
        test = h
        start = h
        end = format(int(h, 16) + 10, 'x')
        self.assertFalse(node._in_range_ei(test, start, end))
        # start<test=end
        test = h
        start = format(int(h, 16) - 10, 'x')
        end = h
        self.assertTrue(node._in_range_ei(test, start, end))
        # test<start<end
        test = h
        start = format(int(h, 16) + 10, 'x')
        end = format(int(h, 16) + 20, 'x')
        self.assertFalse(node._in_range_ei(test, start, end))
        # start>end, test is in
        test = format(1, '040x')
        start = h
        end = format(int(h, 16)//2, 'x')
        self.assertTrue(node._in_range_ei(test, start, end))

    def test_in_range_ee(self):
        '''
        test the (start, end]
        '''
        h = 'b444ac06613fc8d63795be9ad0beaf55011936ac'
        node = Node(h)
        # start==end
        test = h
        start = h
        end = h
        self.assertFalse(node._in_range_ee(test, start, end))
        # end = start + 1
        test = h
        start = h
        end = format(int(h, 16) + 1, 'x')
        self.assertFalse(node._in_range_ee(test, start, end))
        # start<test<end
        test = h
        start = format(int(h, 16) - 10, 'x')
        end = format(int(h, 16) + 10, 'x')
        self.assertTrue(node._in_range_ee(test, start, end))
        # start=h<end
        test = h
        start = h
        end = format(int(h, 16) + 10, 'x')
        self.assertFalse(node._in_range_ee(test, start, end))
        # start<test=end
        test = h
        start = format(int(h, 16) - 10, 'x')
        end = h
        self.assertFalse(node._in_range_ee(test, start, end))
        # test<start<end
        test = h
        start = format(int(h, 16) + 10, 'x')
        end = format(int(h, 16) + 20, 'x')
        self.assertFalse(node._in_range_ee(test, start, end))
        # start>end, test is in
        test = format(1, '040x')
        start = h
        end = format(int(h, 16)//2, 'x')
        self.assertTrue(node._in_range_ee(test, start, end))

    def test_format(self):
        node = Node('0000000000000000000000000000000000000000')
        h = node._format(10)
        self.assertEqual(h, '000000000000000000000000000000000000000a')

    def test_add(self):
        node = Node('0000000000000000000000000000000000000000')
        h = node._add(node._id, -1)
        self.assertEqual(h, 'ffffffffffffffffffffffffffffffffffffffff')

    @patch('requests.post')
    def test_join(self, post_mock):
        '''
        Use the example in paper.
        '''
        # set up mock server
        ms = MockServer()
        post_mock.side_effect = lambda url, json : ms.post(url, json)
        # set up smaller ring
        ct.RING_SIZE_BIT = 3
        ct.init()
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
        self.assertEqual(node_0._table.get_node(1), node_3._id) # node 0 status
        self.assertEqual(node_0._table.get_node(2), node_3._id)
        self.assertEqual(node_0._table.get_node(3), node_0._id)
        self.assertEqual(node_0.find_predecessor(node_0._id), node_3._id)
        self.assertEqual(node_3._table.get_node(1), node_0._id) # node 3 status
        self.assertEqual(node_3._table.get_node(2), node_0._id)
        self.assertEqual(node_3._table.get_node(3), node_0._id)
        self.assertEqual(node_3.find_predecessor(node_3._id), node_0._id)
        # test 3: join node 1 to the ring
        node_1 = Node('1')
        ms.add_node(node_1._id, node_1)
        node_1.join(node_3._id)
        self.assertEqual(node_0._table.get_node(1), node_1._id) # node 0 status
        self.assertEqual(node_0._table.get_node(2), node_3._id)
        self.assertEqual(node_0._table.get_node(3), node_0._id)
        self.assertEqual(node_0.find_predecessor(node_0._id), node_3._id)
        self.assertEqual(node_3._table.get_node(1), node_0._id) # node 3 status
        self.assertEqual(node_3._table.get_node(2), node_0._id)
        self.assertEqual(node_3._table.get_node(3), node_0._id)
        self.assertEqual(node_3.find_predecessor(node_3._id), node_0._id)
        self.assertEqual(node_1._table.get_node(1), node_3._id) # node 1 status
        self.assertEqual(node_1._table.get_node(2), node_3._id)
        self.assertEqual(node_1._table.get_node(3), node_0._id)
        self.assertEqual(node_1.find_predecessor(node_1._id), node_0._id)

if __name__ == '__main__':
    unittest.main()
