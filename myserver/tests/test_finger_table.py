import hashlib
import unittest
import myserver.mychord.constants as ct
from myserver.mychord.finger_table import FingerTable

class TestFingerTable(unittest.TestCase):
    
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

    def test_index_size(self):
        m = hashlib.sha1()
        m.update(b'test1')
        h = m.hexdigest()
        ft = FingerTable(h)
        self.assertTrue(ft.get_start(1))
        self.assertTrue(ft.get_start(ct.RING_SIZE_BIT))
        self.assertFalse(ft.get_start(0))
        self.assertFalse(ft.get_start(ct.RING_SIZE_BIT + 1))

    def test_rw_node(self):
        m = hashlib.sha1()
        m.update(b'test1')
        h = m.hexdigest()
        ft = FingerTable(h)
        m = hashlib.sha1()
        m.update(b'test2')
        node = m.hexdigest()
        self.assertFalse(ft.get_node(1))
        self.assertTrue(ft.set_node(1, node))
        self.assertEqual(ft.get_node(1), node)

if __name__ == '__main__':
    unittest.main()
