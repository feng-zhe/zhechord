'''
This file contains code for chord ring
Reference:
[1] https://en.wikipedia.org/wiki/Chord_(peer-to-peer)
[2] paper by Ion Stoica*
'''
import hashlib
import requests
import finger_table as ft
import constants as ct

class Node(object):
    '''
    This node represents a node(server) in chord ring.
    '''
    def __init__(self, identity):
        '''
        Initialze:

        self._id:   The identity of this node.
        self._predecessor:    The predecessor of this node.
        self._table:    The finger_table of this node.

        Be aware that the successor is the finger[1].node.

        Args:
            identity:   The identity of this node.

        Returns:
            N/A

        Raises:
            N/A
        '''
        self._id = identity
        self._predecessor = None
        self._table = ft.FingerTable(identity)

    def find_successor(self, identity):
        '''
        Ask this node to find the successor of the identity.

        Args:
            identity:   The identity of the object.
                        If None, return this nodes own successor.

        Returns:
            The identity of the successor in hex.

        Raises:
            N/A
        '''
        pred = self.find_predecessor(identity)
        return self.remote_find_successor(pred, pred)

    def find_predecessor(self, identity):
        '''
        Ask this node to find the predecessor of identity.

        Args:
            identity:   The identity of the object.

        Returns:
            The identity of the predecessor.

        Raises:
            N/A
        '''
        node = self._id
        succ = self._table.get_node(1)
        while not self._in_range_ei(identity, node, succ):
            node = self.remote_closest_preceding_finger(node, identity)
            succ = self.remote_find_successor(node, node)
        return node

    def closest_preceding_finger(self, identity):
        '''
        Return the closest finger preceding id

        Args:
            identity:   The identity of the object.

        Returns:
            The identity of the closest finger preceding id.

        Raises:
            N/A
        '''
        for i in range(ct.RING_SIZE_BIT, 0, -1):
            fnode = self._table.get_node(i)
            start = format((int(self._id, 16) + 1) % ct.ID_MAX, 'x')
            if self._in_range_ee(fnode, start, identity):
                return fnode
        return self._id

    def join(self, remote_node):
        '''
        Create/join a chord ring.

        Args:
            remote_node:   The identity of the node which is already in the ring.
                    If None, create a new ring.

        Returns:
            N/A

        Raises:
            N/A
        '''
        if remote_node:        # join a ring via node
            self.init_finger_table(remote_node)
            self.update_others()
        else:       # the first one in the ring
            self._predecessor = self._id
            for i in range(1, ct.RING_SIZE_BIT+1):
                self._table.set_node(1, self._id)

    def init_finger_table(self, remote_node):
        '''
        Initialize the calling node's finger table by the remote_node.

        Args:
            remote_node:    The remote node id.

        Returns:
            N/A

        Raises:
            N/A
        '''
        successor = self.remote_find_successor(remote_node, 
                                self._table.get_start(1))
        self._table.set_node(1, successor)
        self._predecessor = self.remote_find_predecessor(successor, successor)
        self.remote_set_predecessor(successor, self._id)
        for i in range(1, ct.RING_SIZE_BIT):
            start = self._table.get_start(i+1)
            fnode = self._table.get_node(i)
            if self._in_range_ie(start, self._id, fnode):
                self._table.set_node(i+1, fnode)
            else:
                remote_succ = self.remote_find_successor(remote_node, start)
                self._table.set_node(i+1, remote_succ)
            
    def update_others(self):
        '''
        Update all nodes whose finger tables should refer to n

        Args:
            N/A

        Returns:
            N/A

        Raises:
            N/A
        '''
        for i in range(1, ct.RING_SIZE_BIT+1):
            # find last node p whose ith finger MIGHT be n
            int_val = int(self._id, 16) - ct.TWO_EXP[i-1]
            p = self.find_predecessor(format(int_val, 'x'))
            self.remote_update_finger_table(p, self._id, i)

    def update_finger_table(self, s, i):
        '''
        If s is i^th finger of n, update n’s finger table with s

        Args:
            s:  The new id.
            i:  Finger table entry index.

        Returns:
            N/A

        Raises:
            N/A
        '''
        if self._in_range_ie(s, self._id, self._table.get_node(i)):
            self._table.set_node(i, s)
            self.remote_update_finger_table(self._predecessor, s, i)

    def get_predecessor(self):
        '''
        Get the predecessor of this current node.

        Args:
            N/A

        Returns:
            The id of the predecessor.

        Raises:
            N/A
        '''
        return self._predecessor

    def set_predecessor(self, identity):
        '''
        Set the precessor of this current node.

        Args:
            identity:   The identity of the predecessor.

        Returns:
            N/A

        Raises:
            N/A
        '''
        self._predecessor = identity

    def remote_find_predecessor(self, remote_node, identity):
        '''
        Find the predecessor of the identity on remote node.

        Args:
            remote_node:    The remote node id.
            identity:       The identity to look up.

        Returns:
            The id of the predecessor.

        Raises:
            requests.exceptions.ConnectionError
            AssertionError
            KeyError
        '''
        url = 'http://{}/find_predecessor'.format(remote_node)
        data = { 'id': identity }
        r = requests.post(url, data=data).json()
        assert(r.status_code==200)
        return r['id']

    def remote_set_predecessor(self, remote_node, identity):
        '''
        Set the predecessor of the remote_node.

        Args:
            remote_node:    The remote node id.
            identity:       The new predecessor identity.

        Returns:
            The id of the predecessor.

        Raises:
            AssertionError
        '''
        url = 'http://{}/set_predecessor'.format(remote_node)
        data = { 'id': identity if identity else self._id }
        r = requests.post(url, data=data)
        assert(r.status_code==200)
        return
    
    def remote_find_successor(self, remote_node, identity):
        '''
        Ask the remote node to find the successor of identity

        Args:
            remote_node:    The remote node id.
            identity:       The identity to loop up.

        Returns:
            The id of the successor.

        Raises:
            N/A
        '''
        # TODO
        pass

    def remote_closest_preceding_finger(self, remote_node, identity):
        '''
        Ask the remote node to return the closest finger preceding id.

        Args:
            identity:   The identity of the object.

        Returns:
            The identity of the closest finger preceding id on remote node.

        Raises:
            N/A
        '''
        # TODO
        pass

    def remote_update_finger_table(self, remote_node, s, i):
        '''
        On remote node, if s is i^th finger of n, update n’s finger table with s.

        Args:
            remote_node:    The remote node id.
            s:  The new id.
            i:  Finger table entry index.

        Returns:
            N/A

        Raises:
            N/A
        '''
        # TODO
        pass

    def _in_range_ie(self, node, start, end):
        '''
        Test whether the node is in [start, end). It will handle the wrap around problem.
        'i' stands for including the start, 'e' stands for excluding the end.

        Args:
            node:   The node to be tested.
            start:  The range start, included.
            end:    The range end, excluded.

        Returns:
            True if in range. False otherwise.

        Raises:
            N/A
        '''
        n_int = int(node, 16)
        s_int = int(start, 16)
        e_int = int(end, 16)
        if s_int > e_int:       # wrap around
            e_int += ct.TWO_EXP[ct.RING_SIZE_BIT]
        elif s_int == e_int:      # empty set
            return False
        return s_int <= n_int < e_int

    def _in_range_ei(self, node, start, end):
        '''
        Test whether the node is in (start, end]. It will handle the wrap around problem.

        Args:
            node:   The node to be tested.
            start:  The range start, included.
            end:    The range end, excluded.

        Returns:
            True if in range. False otherwise.

        Raises:
            N/A
        '''
        n_int = int(node, 16)
        s_int = int(start, 16)
        e_int = int(end, 16)
        if s_int > e_int:       # wrap around
            e_int += ct.TWO_EXP[ct.RING_SIZE_BIT]
        elif s_int == e_int:      # empty set
            return False
        return s_int < n_int <= e_int

    def _in_range_ee(self, node, start, end):
        '''
        Test whether the node is in (start, end). It will handle the wrap around problem.

        Args:
            node:   The node to be tested.
            start:  The range start, included.
            end:    The range end, excluded.

        Returns:
            True if in range. False otherwise.

        Raises:
            N/A
        '''
        n_int = int(node, 16)
        s_int = int(start, 16)
        e_int = int(end, 16)
        if s_int > e_int:       # wrap around
            e_int += ct.TWO_EXP[ct.RING_SIZE_BIT]
        if e_int - s_int <= 1:      # empty set
            return False
        return s_int < n_int < e_int

    # Advanced
    # def stablize(self):
        # '''
        # Periodically verify n’s immediate successor, and tell the successor about n

        # Args:
            # N/A

        # Returns:
            # N/A

        # Raises:
            # N/A
        # '''
        # # TODO
        # pass

    # def notify(self, remote_node):
        # '''
        # The remote node thinks it might be our predecessor.

        # Args:
            # remote_node:   the remote node notifying this node.

        # Returns:
            # N/A

        # Raises:
            # N/A
        # '''
        # # TODO
        # pass

    # def fix_fingers(self):
        # '''
        # Periodically refresh finger table entries.

        # Args:
            # N/A

        # Returns:
            # N/A

        # Raises:
            # N/A
        # '''
        # # TODO
        # pass
