'''
This file contains code for finger table implementation.
'''
from . import constants as ct
from . import helper as helper

class FingerTable(object):
    '''
    Finger table class.
    '''

    def __init__(self, node_id):
        '''
        Initialize the finger table.
        To use the same annotation in paper, the index starts from 1.
        
        self._table:    A map representing the internal finger table.
                        The value of each item is an FingerTableEntry.

        Args:
            node_id:    The id of the node which has this table.

        Returns:
            N/A

        Raises:
            N/A
        '''
        self._table = {}
        for i in range(1, ct.RING_SIZE_BIT+1):     # i can be RING_SIZE_BIT
            self._table[i] = _FingerTableEntry(node_id, i)

    def get_start(self, i):
        '''
        Get the finger[i].start.
        
        Args:
            i:  The index of the entry.

        Returns:
            The finger[i].start in hex.
            Otherwise None.

        Raises:
            N/A
        '''
        if i < 1 or i > ct.RING_SIZE_BIT:
            return None

        return self._table[i].start

    def get_interval(self, i):
        '''
        Get the finger[i].interval.
        
        Args:
            i:  The index of the entry.

        Returns:
            A tuple (finger[i].start, finger[i+1].start). All in hex.
            Otherwise None.

        Raises:
            N/A
        '''
        if i < 1 or i > ct.RING_SIZE_BIT:
            return None

        return (self._table[i].start, self._table[i+1].start)

    def get_node(self, i):
        '''
        Get the finger[i].node.
        
        Args:
            i:  The index of the entry.

        Returns:
            The identity of the finger[i].node.
            Otherwise None.

        Raises:
            N/A
        '''
        if i < 1 or i > ct.RING_SIZE_BIT:
            return None

        return self._table[i].node

    def set_node(self, i, node):
        '''
        Set the finger[i].node.
        
        Args:
            i:  The index of the entry.

        Returns:
            True if success, False otherwise.

        Raises:
            N/A
        '''
        if i < 1 or i > ct.RING_SIZE_BIT:
            return False

        self._table[i].node = node
        return True

class _FingerTableEntry(object):
    '''
    Finger table entry class.
    '''

    def __init__(self, node_id, i):
        '''
        Initializate the following values:
        self.start: the start of the interval
        self.node: the first node >= self.start

        Args:
            node_id:    A hex string. The id of the node in which the table is.
            i:  A integer. The index of the entry. From 1 to the length of the identity in bits (160).

        Returns:
            N/A

        Raises:
            N/A
        '''
        self.start = helper._add(node_id, ct.TWO_EXP[i-1])
        self.node = None
