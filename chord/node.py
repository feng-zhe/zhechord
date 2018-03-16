'''
This file contains code for chord ring
Reference:
[1] https://en.wikipedia.org/wiki/Chord_(peer-to-peer)
[2] paper by Ion Stoica*
'''

class Node(object):
    '''
    This node represents a node(server) in chord ring.
    '''
    def calc_id(self, name):
        '''
        Calculate the id (SHA1 hash) of name.

        Args:
            name:   a string to be hashed

        Returns:
            The SHA1 hashed value.

        Raises:
            N/A
        '''
        # TODO
        pass 

    def create_chord(self):
        '''
        Create a new chord ring from itself.

        Args:
            N/A

        Returns:
            N/A

        Raises:
            N/A
        '''
        # TODO
        pass

    def join(self, node):
        '''
        Join a chord ring.

        Args:
            node:   A node which is already in the ring.

        Returns:
            N/A

        Raises:
            N/A
        '''
        # TODO
        pass

    def find_successor(self, identity):
        '''
        Find the successor of this node.

        Args:
            node:   A node which is already in the ring.

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

    def initial_finger_table(self):
        '''
        Initialize the calling node's finger table.

        Args:
            N/A

        Returns:
            N/A

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

    def stablize(self):
        '''
        Periodically verify n’s immediate successor, and tell the successor about n

        Args:
            N/A

        Returns:
            N/A

        Raises:
            N/A
        '''
        # TODO
        pass

    def notify(self, node):
        '''
        The node thinks it might be our predecessor

        Args:
            node:   the node notifying this node.

        Returns:
            N/A

        Raises:
            N/A
        '''
        # TODO
        pass

    def fix_fingers(self):
        '''
        Periodically refresh finger table entries

        Args:
            N/A

        Returns:
            N/A

        Raises:
            N/A
        '''
        # TODO
        pass
