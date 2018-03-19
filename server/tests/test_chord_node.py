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
        # set up mock server
        ms = MockServer()
        post_mock.side_effect = lambda url, json : ms.post(url, json)
        # set up smaller ring
        ct.RING_SIZE_BIT = 3
        ct.init()
        # test 1: node 1 creates a new ring
        node_1 = Node('0')
        ms.add_node(node_1._id, node_1)       # add this node to mocked server
        node_1.join()
        for i in range(1, ct.RING_SIZE_BIT+1):      # should point to itself
            self.assertEqual(
                    node_1._table.get_node(i), 
                    node_1._id)
        # test 2: join node 2 to then ring
        node_2 = Node('3')
        ms.add_node(node_2._id, node_2)
        node_2.join(node_1._id)
        # node 1 status
        self.assertEqual(node_1._table.get_node(1), node_2._id)
        self.assertEqual(node_1._table.get_node(2), node_2._id)
        self.assertNotEqual(node_1._table.get_node(3), node_2._id)
        self.assertEqual(node_1.find_predecessor(node_1._id), node_2._id)
        # node 2 status
        self.assertEqual(node_2._table.get_node(1), node_1._id)
        self.assertEqual(node_2._table.get_node(2), node_1._id)
        self.assertEqual(node_2._table.get_node(3), node_1._id)
        self.assertEqual(node_2.find_predecessor(node_2._id), node_1._id)
        # test 3: join node 3 to the ring
        # TODO

if __name__ == '__main__':
    unittest.main()
