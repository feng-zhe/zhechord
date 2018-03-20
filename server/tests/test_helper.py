import unittest
import mychord.helper as helper
import mychord.constants as ct

class TestHelper(unittest.TestCase):
    
    def test_format(self):
        ct.RING_SIZE_BIT = 160
        ct.init()
        h = helper._format(10)
        self.assertEqual(h, '000000000000000000000000000000000000000a')

    def test_add(self):
        h = helper._add('0000000000000000000000000000000000000000', -1)
        self.assertEqual(h, 'ffffffffffffffffffffffffffffffffffffffff')

if __name__ == '__main__':
    unittest.main()
