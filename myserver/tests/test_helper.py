import unittest
import myserver.mychord.helper as helper
import myserver.mychord.constants as ct

class TestHelper(unittest.TestCase):
    
    _default_size = 0

    @classmethod
    def setUpClass(cls):
        '''
        Set up chord ring size for this test.
        '''
        cls._default_size = ct.RING_SIZE_BIT
        ct.RING_SIZE_BIT = 160
        ct.init()

    @classmethod
    def tearDownClass(cls):
        '''
        Restore chord ring default size.
        '''
        ct.RING_SIZE_BIT = cls._default_size
        ct.init()

    def test_format(self):
        h = helper._format(10)
        self.assertEqual(h, '000000000000000000000000000000000000000a')

    def test_add(self):
        h = helper._add('0000000000000000000000000000000000000000', -1)
        self.assertEqual(h, 'ffffffffffffffffffffffffffffffffffffffff')

    def test_gen_net_id(self):
        test_id = 'aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa'
        net_id = helper._gen_net_id(test_id)
        self.assertEqual(net_id, ct.CONTAINER_PREFIX + test_id)

if __name__ == '__main__':
    unittest.main()
