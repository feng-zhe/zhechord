'''
This file contains code for chord ring
Reference:
[1] https://en.wikipedia.org/wiki/Chord_(peer-to-peer)
[2] paper by Ion Stoica*
'''
import hashlib
import logging
import random
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
        self._table = ft.FingerTable(identity) # finger table
        self._data = {}                        # key-value store

    #-------------------------------------- start of local part --------------------------------------
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
            remote_node:    The identity of the node which is already in the ring.
                            If None, create a new ring.

        Returns:
            N/A

        Raises:
            N/A
        '''
        if remote_node:        # join a ring via node
            logger.debug('({}) join a ring via {}'
                    .format(self._id, remote_node))
            self._predecessor = None
            succ = self.remote_find_successor(remote_node, self._id)
            self.set_successor(succ)
            # mine: check whether the remote node's successor is itself
            # if so, it means this node is the init node and not initialized.
            # Then we init it's successor as "seed" and it will self-correct them.
            if remote_node == self.remote_get_successor(remote_node):
                self.remote_set_successor(remote_node, self._id)
            # end of mine
        else:       # mine: the first one in the ring
            logger.debug('({}) create a new ring'.format(self._id))
            self._predecessor = None        # be consistent
            for i in range(1, ct.RING_SIZE_BIT+1):
                self._table.set_node(i, self._id)
            # end of mine

    def stabilize(self):
        '''
        Periodically verify n’s immediate successor, and tell the successor about n
        This function may change the successor and trigger notify().

        Args:
            N/A

        Returns:
            N/A

        Raises:
            N/A
        '''
        logger.debug('({}) stablizing'.format(self._id))
        succ = self.get_successor()
        x = self.remote_get_predecessor(succ)
        if self._in_range_ee(x, self._id, self.get_successor()):
            self.set_successor(x)
        succ = self.get_successor()
        self.remote_notify(succ, self._id)
        logger.debug('({}) stablizing -> Done'.format(self._id))

    def notify(self, remote_node):
        '''
        The remote node thinks it might be our predecessor.
        This function only changes predecessor if ok.

        Args:
            remote_node:   the remote node notifying this node.

        Returns:
            N/A

        Raises:
            N/A
        '''
        logger.debug('({}) notified by {}'
                .format(self._id, remote_node))
        if self._predecessor == None or \
                self._in_range_ee(
                remote_node, 
                self._predecessor, 
                self._id):
            self._predecessor = remote_node
            logger.debug('({0}) notified by {1} -> Done and changed predecesor to {1}'
                    .format(self._id, remote_node))
        else:
            logger.debug('({}) notified by {} -> Done but not changed'
                    .format(self._id, remote_node))

    def fix_fingers(self, loop=False):
        '''
        Periodically refresh finger table entries.
        This function only changes the finger table.

        Args:
            loop:   A boolean flag. If True, then loop.
                    Otherwise, use random.

        Returns:
            N/A

        Raises:
            N/A
        '''
        logger.debug('({}) fixing finger table'.format(self._id))
        if loop:
            for i in range(1, ct.RING_SIZE_BIT+1):
                succ = self.find_successor(self._table.get_start(i))
                self._table.set_node(i, succ)
                logger.debug('({}) set finger index {} with node {}'
                        .format(self._id, i, succ))
        else:
            i = random.randint(1, ct.RING_SIZE_BIT)
            succ = self.find_successor(self._table.get_start(i))
            self._table.set_node(i, succ)
            logger.debug('({}) set finger index {} with node {}'
                    .format(self._id, i, succ))
        logger.debug('({}) fixing finger table -> Done'.format(self._id))

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

    def set_successor(self, identity):
        '''
        Set the successor of this current node.

        Args:
            identity:   The new successor id.

        Returns:
            The id of the successor.

        Raises:
            N/A
        '''
        self._table.set_node(1, identity)

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

    def put(self, key, value):
        '''
        Put the key-value into the ring.

        Args:
            key:    The key of the key-value pair.
            value:  The value of key-value pair.

        Returns:
            N/A

        Raises:
            N/A
        '''
        key_id = helper._hash(key)
        succ = self.find_successor(key_id)
        if succ == self._id:
            self._data[key] = value
        else:
            self.remote_put(succ, key, value)

    def get(self, key):
        '''
        Put the key into the ring.

        Args:
            key:    The key of the key-value pair.

        Returns:
            The value of the key-value pair.
            If there isn't, return None.

        Raises:
            N/A
        '''
        key_id = helper._hash(key)
        succ = self.find_successor(key_id)
        if succ == self._id:
            return self._data.get(key)
        else:
            return self.remote_get(succ, key)
    #-------------------------------------- end of local part --------------------------------------

    #-------------------------------------- start of remote part --------------------------------------
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
        if remote_node == self._id:     # if self, call self
            return self.find_predecessor(identity)
        url = 'http://{}:8000/find_predecessor'\
                .format(helper._gen_net_id(remote_node))
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
        if remote_node == self._id:     # if self, call self
            pred =  self.get_predecessor()
        else:
            url = 'http://{}:8000/get_predecessor'\
                    .format(helper._gen_net_id(remote_node))
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
            N/A

        Raises:
            requests.exceptions.ConnectionError
            AssertionError
        '''
        logger.debug('({}) ask {} to set its predecessor as {}'
                        .format(self._id, remote_node, identity))
        if remote_node == self._id:     # if self, call self
            self.set_predecessor(identity)
        else:
            url = 'http://{}:8000/set_predecessor'\
                    .format(helper._gen_net_id(emote_node))
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
        if remote_node == self._id:     # if self, call self
            succ = self.get_successor()
        else:
            url = 'http://{}:8000/get_successor'\
                    .format(helper._gen_net_id(remote_node))
            payload = {}
            r = requests.post(url, json=payload)
            assert(r.status_code==200)
            succ = r.json()['id']
        logger.debug('({}) ask {} for its own successor -> {}'
                        .format(self._id, remote_node, succ))
        return succ

    def remote_set_successor(self, remote_node, identity):
        '''
        Set the successor of the remote_node.

        Args:
            remote_node:    The remote node id.
            identity:       The new successor identity.

        Returns:
            N/A

        Raises:
            requests.exceptions.ConnectionError
            AssertionError
        '''
        logger.debug('({}) ask {} to set its successor as {}'
                        .format(self._id, remote_node, identity))
        if remote_node == self._id:     # if self, call self
            self.set_successor(identity)
        else:
            url = 'http://{}:8000/set_successor'\
                    .format(helper._gen_net_id(remote_node))
            payload = { 'id': identity }
            r = requests.post(url, json=payload)
            assert(r.status_code==200)
        logger.debug('({}) ask {} to set its successor as {} is done'
                        .format(self._id, remote_node, identity))
        return

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
        if remote_node == self._id:     # if self, call self
            succ = self.find_successor(identity)
        else:
            url = 'http://{}:8000/find_successor'\
                    .format(helper._gen_net_id(remote_node))
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
            remote_node:    The remote node identity.
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
        if remote_node == self._id:     # if self, call self
            cpt = self.closest_preceding_finger(identity)
        else:
            url = 'http://{}:8000/closest_preceding_finger'\
                    .format(helper._gen_net_id(remote_node))
            payload = { 'id': identity }
            r = requests.post(url, json=payload)
            assert(r.status_code==200)
            cpt = r.json()['id']
        logger.debug('({}) ask {} to find closest preceding finger of {} -> {}'
                        .format(self._id, remote_node, identity, cpt))
        return cpt

    def remote_notify(self, remote_node, identity):
        '''
        Ask the remote node to run the notify with identity.
        
        Args:
            remote_node:    The identity of the remote node.
            identity:   The identity of the object.

        Returns:
            N/A

        Raises:
            requests.exceptions.ConnectionError
            AssertionError
        '''
        logger.debug('({}) notify {}'.format(self._id, remote_node))
        if remote_node == self._id:     # if self, call self
            self.notify(identity)
        else:
            url = 'http://{}:8000/notify'\
                    .format(helper._gen_net_id(remote_node))
            payload = { 'id': identity }
            r = requests.post(url, json=payload)
            assert(r.status_code==200)
        logger.debug('({}) notify {} -> Done!'.format(self._id, remote_node))

    def remote_put(self, remote_node, key, value):
        '''
        Ask the remote node to put the key.

        Args:
            remote_node:    The remote node identity.
            key:    The key.
            value:  The value.

        Returns:
            N/A

        Raises:
            N/A
        '''
        logger.debug('({}) ask {} to put key {} value {}'\
                .format(self._id, remote_node, key, value))
        if remote_node == self._id:     # if self, call self
            self.put(key, value)
        else:
            url = 'http://{}:8000/put'\
                    .format(helper._gen_net_id(remote_node))
            payload = { 'key': key, 'value': value }
            r = requests.post(url, json=payload)
            assert(r.status_code==200)
        logger.debug('({}) ask {} to put key {} value {} -> Done'\
                .format(self._id, remote_node, key, value))

    def remote_get(self, remote_node, key):
        '''
        Ask the remote node to get the value for the key.
        
        Args:
            remote_node:    The identity of the remote node.
            key:    The key of the key-value pair.

        Returns:
            The value of the key-value pair.

        Raises:
            N/A
        '''
        logger.debug('({}) ask {} to get key {}'\
                .format(self._id, remote_node, key))
        if remote_node == self._id:     # if self, call self
            self.get(key)
        else:
            url = 'http://{}:8000/get'.format(helper._gen_net_id(remote_node))
            payload = { 'key': key }
            r = requests.post(url, json=payload)
            assert(r.status_code==200)
            value = r.json()['value']
        logger.debug('({}) ask {} to get key {} -> value {}'\
                .format(self._id, remote_node, key, value))
    #-------------------------------------- end of remote part --------------------------------------

    #-------------------------------------- start of internal part --------------------------------------
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
        if not node or not start or not end:
            return False
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
        if not node or not start or not end:
            return False
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
        if not node or not start or not end:
            return False
        n_int = int(node, 16)
        s_int = int(start, 16)
        e_int = int(end, 16)
        if s_int > e_int:       # wrap around
            return s_int < n_int < ct.TWO_EXP[ct.RING_SIZE_BIT] \
                    or 0 <= n_int < e_int
        if e_int - s_int <= 1:      # empty set
            return False
        return s_int < n_int < e_int
    #-------------------------------------- end of internal part --------------------------------------
