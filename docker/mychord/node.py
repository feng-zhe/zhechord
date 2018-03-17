'''
This file contains code for chord ring
Reference:
[1] https://en.wikipedia.org/wiki/Chord_(peer-to-peer)
[2] paper by Ion Stoica*
'''
import hashlib
import mychord.finger_table as ft

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

    def find_successor(self, identity):
        '''
        Find the successor of this node.

        Args:
            identity:   The identity of the object.

        Returns:
            The identity of the successor in hex.

        Raises:
            N/A
        '''
        # TODO
        pass

    def find_predecessor(self, identity):
        '''
        Find the predecessor for identity.

        Args:
            identity:   The identity of the object.

        Returns:
            The identity of the predecessor in hex.

        Raises:
            N/A
        '''
        # TODO
        pass

    def closest_preceding_node(self, identity):
        '''
        Return the closest finger preceding id

        Args:
            identity:   The identity of the object.

        Returns:
            The identity of the closest finger preceding id.

        Raises:
            N/A
        '''
        # TODO
        pass

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
        self._predecessor = self.remote_get_predecessor(successor)
        self.remote_set_predecessor(successor, self._id)
        for i in range(1, ct.RING_SIZE_BIT):
            start = self._table.get_start(i+1)
            fnode = self._table.get_node(i)
            if self._in_range(start, self._id, fnode):
                self._table.set_node(i+1, fnode)
            else:
                remote_succ = self.remote_find_successor(remote_node, start)
                self._table.set_node(i+1, remote_succ)
            
    def _in_range(self, node, start, end):
        '''
        Test whether the node is in [start, end).
        It will handle the wrap around problem.

        Args:
            node:   The node to be tested.
            start:  The range start, included.
            end:    The range end, excluded.

        Returns:
            True if in range. False otherwise.

        Raises:
            N/A
        '''
        # TODO
        pass

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
        # TODO
        pass

    def update_finger_table(self, s, i):
        '''
        If s is i^th finger of n, update n’s finger table with s
        TODO
        '''
        # TODO
        pass

    def remote_find_successor(self, remote_node, identity):
        '''
        Ask the remote node to find the successor of this node.

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

    def remote_get_predecessor(self, remote_node):
        '''
        Get the predecessor of the remote_node.

        Args:
            remote_node:    The remote node id.

        Returns:
            The id of the predecessor.

        Raises:
            N/A
        '''
        # TODO
        pass

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

    def remote_set_predecessor(self, remote_node, identity):
        '''
        Set the predecessor of the remote_node.

        Args:
            remote_node:    The remote node id.
            identity:       The new predecessor identity.

        Returns:
            The id of the predecessor.

        Raises:
            N/A
        '''
        # TODO
        pass

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
