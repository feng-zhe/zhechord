'''
This file contains code for chord ring
Reference:
[1] https://en.wikipedia.org/wiki/Chord_(peer-to-peer)
[2] paper by Ion Stoica*
'''
import logging
import random
import time
import requests
from . import finger_table as ft
from . import constants as ct
from . import helper as helper

logger = logging.getLogger(__name__)

class Node(object):
    '''
    This node represents a node(server) in chord ring.
    '''
    def __init__(self, identity):
        '''
        Initialze:

        self._id:           The identity of this node.
        self._predecessor:  The predecessor of this node.
        self._table:        The finger_table of this node.
                            Be aware that the successor is the finger[1].node.
        self._backup_succ:  A array of the backup successors.

        Args:
            identity:   The identity of this node.

        Returns:
            N/A

        Raises:
            N/A
        '''
        self._id = identity
        self._predecessor = None
        self._table = ft.FingerTable(identity)      # finger table
        self._backup_succ = []      # the backup successor
        self._data = {}     # key-value store

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
        succ = self._id
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
            # init backup successors
            temp_succ = succ
            for i in range(0, ct.BACKUP_SUCC_NUM):
                temp_succ = self.find_successor(helper._add(temp_succ, 1))
                self._backup_succ.append(temp_succ)
            # end of mine
        else:       # mine: the first one in the ring
            logger.debug('({}) create a new ring'.format(self._id))
            self._predecessor = None        # be consistent
            for i in range(1, ct.RING_SIZE_BIT+1):
                self._table.set_node(i, self._id)
            # init backup successors to itself
            for i in range(0, ct.BACKUP_SUCC_NUM):
                self._backup_succ.append(self._id)
            # end of mine

    def stabilize(self):
        '''
        Periodically verify n’s immediate successor, and tell the successor about n
        This function may change the successor and trigger notify().
        According to chord ring's paper, this function is enhanced to also update
        the backup successors.

        Args:
            N/A

        Returns:
            N/A

        Raises:
            N/A
        '''
        logger.debug('({}) stabilizing'.format(self._id))
        # # mine: check predecessor liveness
        if self._predecessor:
            try:
                logger.debug('({}) checking predecessor livenetss'.format(self._id))
                self.remote_get_successor(self._predecessor)
                logger.debug('({}) checking predecessor livenetss -> alive'\
                        .format(self._id))
            except requests.ConnectionError:
                logger.debug('({}) checking predecessor livenetss -> dead'\
                        .format(self._id))
                backup = self._get_alive_backup_succ()
                self._predecessor = backup
                logger.debug('({}) checking predecessor livenetss -> '\
                        'set predecessor as backup {}'\
                        .format(self._id, backup))
        # end of mine
        flag = False
        while not flag:     # mine: try all backup successors
            succ = self.get_successor()     # original
            try:
                x = self.remote_get_predecessor(succ)   # original
                flag = True
            except requests.ConnectionError:    # mine: add fault recovery
                self._remove_dead(succ)
                logger.debug('({}) successor {} is dead,'\
                        'use backup {} instead'.format(
                            self._id, succ, self.get_successor()))
        # mine: check successor's predecessor's liveness
        try:
            # for the init node, the predecessor is None
            if x:
                # original
                self.remote_get_successor(x)
                if self._in_range_ee(x, self._id, self.get_successor()):
                    self.set_successor(x)
                # end of original
        except requests.ConnectionError:    # the predecessor is dead
            pass        # no need for updating
        # end of mine
        succ = self.get_successor()
        try:
            self.remote_notify(succ, self._id)
        except requests.ConnectionError:
            pass        # no need to do anything for a dead node
        # mine: update the backup successors
        self._update_backup_succ()
        # end of mine
        logger.debug('({}) stabilizing -> Done'.format(self._id))

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
            logger.debug('({0}) notified by {1} -> In range ({2},{0})'
                    .format(self._id, remote_node, self._predecessor))
            self._predecessor = remote_node
            logger.debug('({0}) notified by {1} -> Done and changed predecesor to {1}'
                    .format(self._id, remote_node))
        else:
            logger.debug('({0}) notified by {1} -> Not in range ({2},{0})'
                    .format(self._id, remote_node, self._predecessor))
            logger.debug('({}) notified by {} -> Done but not changed'
                    .format(self._id, remote_node))

    def fix_fingers(self, loop=False):
        '''
        Periodically refresh finger table entries.
        This function only changes the finger table.
        Replace the entry with backup if connection error.

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
                try:
                    succ = self.find_successor(self._table.get_start(i))
                    self.remote_get_successor(succ)     # check liveness
                    self._table.set_node(i, succ)
                    logger.debug('({}) set finger index {} with node {}'
                            .format(self._id, i, succ))
                except requests.ConnectionError:
                    # mine: replace with backup
                    backup = self._get_alive_backup_succ()
                    self._table.set_node(i, backup)
                    logger.debug('({}) set finger index {} \
                            -> connection error, use backup {}'
                            .format(self._id, i, succ, backup))
        else:
            i = random.randint(1, ct.RING_SIZE_BIT)
            try:
                succ = self.find_successor(self._table.get_start(i))
                self.remote_get_successor(succ)     # check liveness
                self._table.set_node(i, succ)
                logger.debug('({}) set finger index {} with node {}'
                        .format(self._id, i, succ))
            except requests.ConnectionError:
                # mine: replace with backup
                backup = self._get_alive_backup_succ()
                self._table.set_node(i, backup)
                logger.debug('({}) set finger index {} \
                        -> connection error, use backup {}'
                        .format(self._id, i, succ, backup))
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
            A array of  [predecessor, xxx, xxx, xxx]

        Raises:
            N/A
        '''
        result = [self.get_predecessor()]
        for i in range(1, ct.RING_SIZE_BIT+1):
            result.append(self._table.get_node(i))
        return result

    def local_put(self, key, value):
        '''
        Put the key-value into the ring.
        Only put the key-value on the local node.
        It is the application layer to decide which node to put.

        Args:
            key:    The key of the key-value pair.
            value:  The value of key-value pair.

        Returns:
            N/A

        Raises:
            N/A
        '''
        logger.debug('({}) put key {} value {}'\
                        .format(self._id, key, value))
        self._data[key] = value
        logger.debug('({}) put key {} value {} -> Done'\
                        .format(self._id, key, value))

    def local_get(self, key):
        '''
        Get the value for key from the ring.
        It will only check the local node data. It is
        the application layer to decide which node to call get.

        Args:
            key:    The key of the key-value pair.

        Returns:
            The value of the key-value pair.
            If there isn't, return None.

        Raises:
            N/A
        '''
        logger.debug('({}) get key {}'\
                        .format(self._id, key))
        value = self._data.get(key, None)
        logger.debug('({}) get key {} -> {}'\
                        .format(self._id, key, value))
        return value

    def display_data(self):
        '''
        Return the key-value data.

        Args:
            N/A

        Returns:
            A dict representing key-value pairs.

        Raises:
            N/A
        '''
        return self._data

    def display_backup_succ(self):
        '''
        Return the backup successors.

        Args:
            N/A

        Returns:
            An array of backup successors.

        Raises:
            N/A
        '''
        return self._backup_succ
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
            requests.ConnectionError
            AssertionError
            KeyError
        '''
        logger.debug('({}) ask {} to find predecessor of {}'\
                .format(self._id, remote_node, identity))
        if remote_node == self._id:     # if self, call self
            return self.find_predecessor(identity)
        url = 'http://{}:8000/find_predecessor'\
                .format(helper._gen_net_id(remote_node))
        payload = { 'id': identity }
        r = self._requests_post(url, payload)
        assert(r.status_code==200)
        pred = r.json()['id']
        logger.debug('({}) ask {} to find predecessor of {} -> {}'\
                .format(self._id, remote_node, identity, pred))
        return pred

    def remote_get_predecessor(self, remote_node):
        '''
        Get the predecessor of the remote node.

        Args:
            remote_node:    The remote node id.

        Returns:
            The id of the predecessor.

        Raises:
            requests.ConnectionError
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
            r = self._requests_post(url, payload)
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
            requests.ConnectionError
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
            r = self._requests_post(url, payload)
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
            requests.ConnectionError
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
            r = self._requests_post(url, payload)
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
            requests.ConnectionError
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
            r = self._requests_post(url, payload)
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
            requests.ConnectionError
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
            r = self._requests_post(url, payload)
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
            requests.ConnectionError
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
            r = self._requests_post(url, payload)
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
            requests.ConnectionError
            AssertionError
        '''
        logger.debug('({}) notify {} with {}'.format(self._id, remote_node, identity))
        if remote_node == self._id:     # mine: if self, impossible to be its self predecessor 
            logger.debug('({}) notify {} -> Abort, it cannot be its own predecessor'.format(self._id, remote_node))
        else:
            url = 'http://{}:8000/notify'\
                    .format(helper._gen_net_id(remote_node))
            payload = { 'id': identity }
            r = self._requests_post(url, payload)
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
            requests.ConnectionError
        '''
        logger.debug('({}) ask {} to put key {} value {}'\
                .format(self._id, remote_node, key, value))
        if remote_node == self._id:     # if self, call self
            self.put(key, value)
        else:
            url = 'http://{}:8000/put'\
                    .format(helper._gen_net_id(remote_node))
            payload = { 'key': key, 'value': value }
            r = self._requests_post(url, payload)
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
            requests.ConnectionError
        '''
        logger.debug('({}) ask {} to get key {}'\
                .format(self._id, remote_node, key))
        if remote_node == self._id:     # if self, call self
            value = self.get(key)
        else:
            url = 'http://{}:8000/get'.format(helper._gen_net_id(remote_node))
            payload = { 'key': key }
            r = self._requests_post(url, payload)
            assert(r.status_code==200)
            value = r.json()['value']
        logger.debug('({}) ask {} to get key {} -> value {}'\
                .format(self._id, remote_node, key, value))
        return value

    def _requests_post(self, url, payload, timeout=2):
        '''
        Help function to send requests and retry 3 times.

        Args:
            url:    The target url.
            payload:    The data in post.
            timeout:    The timeout of the request. Default is 2.

        Returns:
            The corresponding object returned by requests.

        Raises:
            requests.ConnectionError
        '''
        correct = False
        r = None
        retry = 0
        while not correct:
            try:
                r = requests.post(url, json=payload, timeout=timeout)
                correct = True
            except requests.exceptions.Timeout:
                retry += 1
                if retry > ct.CONN_RETRY:      # reached max retry times
                    logger.info('max retry times reached. Abort.')
                    raise requests.ConnectionError()
                logger.info('request failed, try again soon.')
                rand_t = random.randint(10,30) / 10
                time.sleep(rand_t)
        return r

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

    def _update_backup_succ(self):
        '''
        Update the backup successors.

        Args:
        Returns:
        Raises:
            N/A
        '''
        temp_succ = self.get_successor()
        for i in range(0, ct.BACKUP_SUCC_NUM):
            try:
                temp_succ = self.find_successor(helper._add(temp_succ, 1))
                self.remote_get_successor(temp_succ)    # check aliveness
                self._backup_succ[i] = temp_succ
            except requests.ConnectionError:    # mine
                pass        # try to wait the ring stable

    def _get_alive_backup_succ(self):
        '''
        Return an alive backup successor.

        Args:
            N/A

        Returns:
            The identity of the alive backup successor.
        
        Raises:
            Exception
        '''
        for i in range(0, ct.BACKUP_SUCC_NUM):
            node = self._backup_succ[i]
            try:
                self.remote_get_successor(node)
                return node
            except requests.ConnectionError:
                pass
        raise Exception('No backup successors alive!')

    def _remove_dead(self, dead_node):
        '''
        Remove the dead node information.
        This function is not mentioned in the chord ring paper.

        Args:
            dead_node:  The identity of the dead_node.

        Returns:
        Raises:
            N/A
        '''
        # update finger table (including successor) with backup
        backup = self._get_alive_backup_succ()
        for i in range(1, ct.RING_SIZE_BIT + 1):
            if self._table.get_node(i) == dead_node:
                self._table.set_node(i, backup)
    #-------------------------------------- end of internal part --------------------------------------
