'''
This file contains code for chord ring
Reference:
[1] https://en.wikipedia.org/wiki/Chord_(peer-to-peer)
[2] paper by Ion Stoica*
'''
import hashlib
import logging
import requests
import mychord.finger_table as ft
import mychord.constants as ct
import mychord.helper as helper

logger = logging.getLogger(__name__)

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

        Returns:
            The identity of the successor in hex.

        Raises:
            N/A
        '''
        logger.debug('({}) finding successor of {}'
                        .format(self._id, identity))
        pred = self.find_predecessor(identity)
        succ = self.remote_get_successor(pred)
        logger.debug('({}) found successor of {} -> {}'
                        .format(self._id, identity, succ))
        return succ

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
        logger.debug('({}) finding predecessor of {}'
                        .format(self._id, identity))
        node = self._id
        succ = self._table.get_node(1)
        while not self._in_range_ei(identity, node, succ):
            cpt = self.remote_closest_preceding_finger(node, identity)
            if cpt == node:     # mine: fix infinite loop issue
                break
            node = cpt
            succ = self.remote_get_successor(node)
        logger.debug('({}) found predecessor of {} -> {}'
                        .format(self._id, identity, node))
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
        logger.debug('({}) finding CPT of {}'.format(self._id, identity))
        for i in range(ct.RING_SIZE_BIT, 0, -1):
            fnode = self._table.get_node(i)
            if self._in_range_ee(fnode, self._id, identity):
                logger.debug('({}) finding CPT of {} -> {}'
                        .format(self._id, identity, fnode))
                return fnode
        logger.debug('({}) finding CPT of {} -> failed, returning itself'
                .format(self._id, identity))
        return self._id

    def join(self, remote_node=None):
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
            logger.debug('({}) join a ring via {}'
                    .format(self._id, remote_node))
            self.init_finger_table(remote_node)
            self.update_others()
        else:       # the first one in the ring
            logger.debug('({}) create a new ring'.format(self._id))
            self._predecessor = self._id
            for i in range(1, ct.RING_SIZE_BIT+1):
                self._table.set_node(i, self._id)

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
        logger.debug('({}) initializing finger table'.format(self._id))
        logger.debug('({}) initializing finger table index {}'
                .format(self._id, 1))
        succ = self.remote_find_successor(remote_node, 
                                self._table.get_start(1))
        self._table.set_node(1, succ)
        logger.debug(('({}) initialized finger table index {} '
                + 'with {}').format(self._id, 1, succ))
        self._predecessor = self.remote_get_predecessor(succ)
        self.remote_set_predecessor(succ, self._id)
        for i in range(1, ct.RING_SIZE_BIT):
            logger.debug('({}) initializing finger table index {}'
                    .format(self._id, i+1))
            start = self._table.get_start(i+1)
            fnode = self._table.get_node(i)
            if self._in_range_ei(start, self._id, fnode):       # mine: fix error finger entry
                logger.debug(('({}) initializing finger table index {}, '
                        + 'same as previous one').format(self._id, i+1))
                self._table.set_node(i+1, fnode)
                logger.debug(('({}) initialized finger table index {} '
                        + 'with {}').format(self._id, i+1, fnode))
            else:
                logger.debug(('({}) initializing finger table index {}, '
                        + 'not same as previous one').format(self._id, i+1))
                remote_succ = self.remote_find_successor(remote_node, start)
                self._table.set_node(i+1, remote_succ)
                logger.debug(('({}) initialized finger table index {} '
                        + 'with {}').format(self._id, i+1, remote_succ))
        logger.debug('({}) initialized finger table'.format(self._id))
            
    def update_others(self):
        '''
        Update all nodes whose finger tables should refer to n

        Based in paper description, it shouldn't update itself.

        Args:
            N/A

        Returns:
            N/A

        Raises:
            N/A
        '''
        logger.debug('({}) updating others'.format(self._id))
        # mine: fix missing update issue
        self.remote_update_finger_table(self._predecessor, self._id, 1)
        for i in range(1, ct.RING_SIZE_BIT+1):
            # find last node p whose ith finger MIGHT be n
            node = helper._add(self._id, - ct.TWO_EXP[i-1])
            p = self.find_predecessor(node)
            if p == self._id:       # mine: fix update itself issue.
                continue
            if self.remote_get_successor(p) == node:        # mine: fix issue when 'node' is a node
                self.remote_update_finger_table(node, self._id, i)
            else:
                self.remote_update_finger_table(p, self._id, i)
        logger.debug('({}) updated others'.format(self._id))

    def update_finger_table(self, s, i):
        '''
        If s is i^th finger of n, update n’s finger table with s
        Original pseudocode has  missing update issue. 
        And be aware of the definition of finger table.

        Args:
            s:  The new id.
            i:  Finger table entry index.

        Returns:
            N/A

        Raises:
            N/A
        '''
        logger.debug('({}) try to update finger table, index {} with {}'
                        .format(self._id, i, s))
        fnode = self._table.get_node(i)
        if self._id == fnode and \
                not self._in_range_ee(s, self._id, fnode):       # mine: fix missing update issue
            self._table.set_node(i, s)
            logger.debug('({}) updated finger table, index {} with {}'
                            .format(self._id, i, s))
        elif self._in_range_ie(s, self._id, fnode):
            self._table.set_node(i, s)
            logger.debug('({}) updated finger table, index {} with {}'
                            .format(self._id, i, s))
            self.remote_update_finger_table(self._predecessor, s, i)
        else:
            logger.debug('({}) not updated finger table, index {} with {}'
                            .format(self._id, i, s))

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

    def get_successor(self):
        '''
        Get the successor of this current node.

        Args:
            N/A

        Returns:
            The id of the sucsessor.

        Raises:
            N/A
        '''
        return self._table.get_node(1)

    def display_finger_table(self):
        '''
        Return the finger table 
        Args:
            N/A

        Returns:
            A array of  [None, xxx, xxx, xxx]

        Raises:
            N/A
        '''
        result = [None]
        for i in range(1, ct.RING_SIZE_BIT+1):
            result.append(self._table.get_node(i))
        return result

    # remote part
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
        url = 'http://{}{}:8000/find_predecessor'.format(ct.CONTAINER_PREFIX, remote_node)
        payload = { 'id': identity }
        r = requests.post(url, json=payload)
        assert(r.status_code==200)
        return r.json()['id']

    def remote_get_predecessor(self, remote_node):
        '''
        Get the predecessor of the remote node.

        Args:
            remote_node:    The remote node id.

        Returns:
            The id of the predecessor.

        Raises:
            requests.exceptions.ConnectionError
            AssertionError
            KeyError
        '''
        logger.debug('({}) ask {} for its own predecessor'
                        .format(self._id, remote_node))
        url = 'http://{}{}:8000/get_predecessor'.format(ct.CONTAINER_PREFIX, remote_node)
        payload = {}
        r = requests.post(url, json=payload)
        pred = r.json()['id']
        assert(r.status_code==200)
        logger.debug('({}) ask {} for its own predecessor -> {}'
                        .format(self._id, remote_node, pred))
        return pred

    def remote_set_predecessor(self, remote_node, identity):
        '''
        Set the predecessor of the remote_node.

        Args:
            remote_node:    The remote node id.
            identity:       The new predecessor identity.

        Returns:
            The id of the predecessor.

        Raises:
            requests.exceptions.ConnectionError
            AssertionError
        '''
        logger.debug('({}) ask {} to set its predecessor as {}'
                        .format(self._id, remote_node, identity))
        url = 'http://{}{}:8000/set_predecessor'.format(ct.CONTAINER_PREFIX,remote_node)
        payload = { 'id': identity }
        r = requests.post(url, json=payload)
        assert(r.status_code==200)
        logger.debug('({}) ask {} to set its predecessor as {} is done'
                        .format(self._id, remote_node, identity))
        return
    
    def remote_get_successor(self, remote_node):
        '''
        Get the successor of the remote node.

        Args:
            remote_node:    The remote node id.

        Returns:
            The id of the successor.

        Raises:
            requests.exceptions.ConnectionError
            AssertionError
            KeyError
        '''
        logger.debug('({}) ask {} for its own successor'
                        .format(self._id, remote_node))
        url = 'http://{}{}:8000/get_successor'.format(ct.CONTAINER_PREFIX, remote_node)
        payload = {}
        r = requests.post(url, json=payload)
        assert(r.status_code==200)
        succ = r.json()['id']
        logger.debug('({}) ask {} for its own successor -> {}'
                        .format(self._id, remote_node, succ))
        return succ

    def remote_find_successor(self, remote_node, identity):
        '''
        Ask the remote node to find the successor of identity

        Args:
            remote_node:    The remote node id.
            identity:       The identity to look up.

        Returns:
            The id of the successor.

        Raises:
            requests.exceptions.ConnectionError
            AssertionError
            KeyError
        '''
        logger.debug('({}) ask {} to find successor of {}'
                        .format(self._id, remote_node, identity))
        url = 'http://{}{}:8000/find_successor'.format(ct.CONTAINER_PREFIX, remote_node)
        payload = { 'id': identity }
        r = requests.post(url, json=payload)
        assert(r.status_code==200)
        succ = r.json()['id']
        logger.debug('({}) ask {} to find successor of {} -> {}'
                        .format(self._id, remote_node, identity, succ))
        return succ

    def remote_closest_preceding_finger(self, remote_node, identity):
        '''
        Ask the remote node to return the closest finger preceding id.

        Args:
            identity:   The identity of the object.

        Returns:
            The identity of the closest finger preceding id on remote node.

        Raises:
            requests.exceptions.ConnectionError
            AssertionError
            KeyError
        '''
        logger.debug('({}) ask {} to find closest preceding finger of {}'
                        .format(self._id, remote_node, identity))
        url = 'http://{}{}:8000/closest_preceding_finger'.format(ct.CONTAINER_PREFIX, remote_node)
        payload = { 'id': identity }
        r = requests.post(url, json=payload)
        assert(r.status_code==200)
        cpt = r.json()['id']
        logger.debug('({}) ask {} to find closest preceding finger of {} -> {}'
                        .format(self._id, remote_node, identity, cpt))
        return cpt

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
            requests.exceptions.ConnectionError
            AssertionError
        '''
        logger.debug('({}) ask {} to update finger table with s={} i={}'
                        .format(self._id, remote_node, s, i))
        url = 'http://{}{}:8000/update_finger_table'.format(ct.CONTAINER_PREFIX, remote_node)
        payload = { 's': s, 'i': i }
        r = requests.post(url, json=payload)
        assert(r.status_code==200)
        return

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
            return s_int <= n_int < ct.TWO_EXP[ct.RING_SIZE_BIT] \
                    or 0 <= n_int < e_int
        elif s_int == e_int:      # empty set
            return False
        else:
            return s_int <= n_int < e_int

    def _in_range_ei(self, node, start, end):
        '''
        Test whether the node is in (start, end]. It will handle the wrap around problem.

        Args:
            node:   The node to be tested.
            start:  The range start, excluded.
            end:    The range end, included.

        Returns:
            True if in range. False otherwise.

        Raises:
            N/A
        '''
        n_int = int(node, 16)
        s_int = int(start, 16)
        e_int = int(end, 16)
        if s_int > e_int:       # wrap around
            return s_int < n_int < ct.TWO_EXP[ct.RING_SIZE_BIT] \
                    or 0 <= n_int <= e_int
        elif s_int == e_int:      # empty set
            return False
        else:
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
            return s_int < n_int < ct.TWO_EXP[ct.RING_SIZE_BIT] \
                    or 0 <= n_int < e_int
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
