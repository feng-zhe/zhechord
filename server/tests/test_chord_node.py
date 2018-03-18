import unittest
from unittest.mock import patch
import mychord.constants as ct
from mychord.node import Node
from tests.mock_server import MockServer

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
        test = format(int(h, 16) + 123456, 'x')
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
        test = format(int(h, 16) + 123456, 'x')
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
        test = format(int(h, 16) + 123456, 'x')
        start = h
        end = format(int(h, 16)//2, 'x')
        self.assertTrue(node._in_range_ee(test, start, end))

    @patch('requests.post')
    def test_join(self, post_mock):
        # set up
        ms = MockServer()
        post_mock.side_effect = lambda url, json : ms.post(url, json)
        id_1 = 'b444ac06613fc8d63795be9ad0beaf55011936ac'
        id_2 = '109f4b3c50d7b0df729d299bc6f8e9ef9066971f'
        # test1: new ring
        node_1 = Node(id_1)
        ms.add_node(id_1, node_1)       # add this node to mocked server
        node_1.join()
        for i in range(1, ct.RING_SIZE_BIT+1):      # should point to itself
            self.assertEqual(
                    node_1._table.get_node(i), 
                    id_1)
        # test2: join to a ring
        node_2 = Node(id_2)
        ms.add_node(id_2, node_2)
        node_2.join(id_1)

if __name__ == '__main__':
    unittest.main()
