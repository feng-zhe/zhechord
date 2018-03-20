import unittest
import logging
import mychord.constants as ct
import mychord.helper as helper
from mychord.node import Node

logging.basicConfig(level=logging.DEBUG)

logger = logging.getLogger(__name__)

class TestNode(unittest.TestCase):
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
        start = helper._add(h, -10)
        end = helper._add(h, 10)
        self.assertTrue(node._in_range_ie(test, start, end))
        # start=h<end
        test = h
        start = h
        end = helper._add(h, 10)
        self.assertTrue(node._in_range_ie(test, start, end))
        # start<h<=end
        test = h
        start = helper._add(h, -10)
        end = h
        self.assertFalse(node._in_range_ie(test, start, end))
        # h<start<end
        test = h
        start = helper._add(h, 10)
        end = helper._add(h, 20)
        self.assertFalse(node._in_range_ie(test, start, end))
        # start>end, h is in
        test = helper._format(1)
        start = h
        end = helper._format(int(h, 16)//2)
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
        start = helper._add(h, -10)
        end = helper._add(h, 10)
        self.assertTrue(node._in_range_ei(test, start, end))
        # start=h<end
        test = h
        start = h
        end = helper._add(h, 10)
        self.assertFalse(node._in_range_ei(test, start, end))
        # start<test=end
        test = h
        start = helper._add(h, -10)
        end = h
        self.assertTrue(node._in_range_ei(test, start, end))
        # test<start<end
        test = h
        start = helper._add(h, 10)
        end = helper._add(h, 20)
        self.assertFalse(node._in_range_ei(test, start, end))
        # start>end, test is in
        test = helper._format(1)
        start = h
        end = helper._format(int(h, 16)//2)
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
        end = helper._add(h, 1)
        self.assertFalse(node._in_range_ee(test, start, end))
        # start<test<end
        test = h
        start = helper._add(h, -10)
        end = helper._add(h, 10)
        self.assertTrue(node._in_range_ee(test, start, end))
        # start=h<end
        test = h
        start = h
        end = helper._add(h, 10)
        self.assertFalse(node._in_range_ee(test, start, end))
        # start<test=end
        test = h
        start = helper._add(h, -10)
        end = h
        self.assertFalse(node._in_range_ee(test, start, end))
        # test<start<end
        test = h
        start = helper._add(h, 10)
        end = helper._add(h, 20)
        self.assertFalse(node._in_range_ee(test, start, end))
        # start>end, test is in
        test = helper._format(1)
        start = h
        end = helper._format(int(h, 16)//2)
        self.assertTrue(node._in_range_ee(test, start, end))

if __name__ == '__main__':
    unittest.main()
