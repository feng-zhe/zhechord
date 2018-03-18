import unittest
import hashlib
from mychord.node import Node

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

if __name__ == '__main__':
    unittest.main()
