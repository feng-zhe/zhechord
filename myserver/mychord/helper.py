import hashlib
import mychord.constants as ct

def _format(value):
    '''
    Format the integer into fixed sized hex string.

    Args:
        value:  An integer value to be formated.

    Returns:
        N/A

    Raises:
        N/A
    '''
    length = ct.RING_SIZE_BIT // 4
    if ct.RING_SIZE_BIT % 4 > 0:
        length += 1
    return format(value, '0{}x'.format(length))

def _add(identity, num):
    '''
    Add the identity by num. It handles neg values and results.

    Args:
        identity:   A hex string. The values to be added.
        num:        An integer. The amount to add.

    Returns:
        A hex string as decreased value.

    Raises:
        N/A
    '''
    val = int(identity, 16) + num
    if val < 0:
        val += ct.TWO_EXP[ct.RING_SIZE_BIT]
    elif val >= ct.TWO_EXP[ct.RING_SIZE_BIT]:
        val %= ct.TWO_EXP[ct.RING_SIZE_BIT]
    return _format(val)

def _gen_net_id(node_id):
    '''
    Generate the network id for the node.

    Args:
        node_id:   The identity of the node.

    Returns:
        The network id for the node.

    Raises:
        N/A
    '''
    return ct.CONTAINER_PREFIX + node_id

def _hash(name):
    '''
    Calculate the identity of the name on the ring, by hashing.

    Args:
        name:   A string to be hashed.
        
    Returns:
        The identity for the key.

    Raises:
        N/A
    '''
    m = hashlib.sha1()
    m.update(name.encode('utf-8'))
    h = m.hexdigest()
    v = int(h, 16) % ct.TWO_EXP[ct.RING_SIZE_BIT]
    return _format(v)
