import hashlib
import unittest
from mychord.finger_table import FingerTable

class TestFingerTable(unittest.TestCase):
    
    def test_index_size(self):
        m = hashlib.sha1()
        m.update(b'test1')
        h = m.hexdigest()
        ft = FingerTable(h)
        self.assertTrue(ft.get_start(1))
        self.assertTrue(ft.get_start(160))
        self.assertFalse(ft.get_start(0))
        self.assertFalse(ft.get_start(161))

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
