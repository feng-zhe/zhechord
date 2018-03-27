import hashlib
import subprocess as sp
import logging
import requests
import tabulate

logger = logging.getLogger(__name__)

IMAGE_NAME = 'fengzhe_chord'
NET_NAME = 'mynet'
CONTAINER_PREFIX = 'cr_'

# def _hash(name):
    # '''
    # Hash the name

    # Args:
        # name:   a string to be hashed
        
    # Returns:
        # The hashed name.

    # Raises:
        # N/A
    # '''
    # m = hashlib.sha1()
    # m.update(name.encode('utf-8'))
    # h = m.hexdigest()
    # return h

def build_image():
    '''
    create the docker image for chord nodes

    Args:
        N/A
        
    Returns:
        N/A

    Raises:
        CalledProcessError
    '''
    # record the old image id, wish it can use cache
    cmd = 'docker images'
    logger.info('Finding old image id, name {}'.format(IMAGE_NAME))
    proc= sp.run(cmd, shell=True, stdout=sp.PIPE, stderr=sp.PIPE)
    old_image_id = ''
    lines = proc.stdout.splitlines()
    for line in lines[1:]:
        words = line.split()
        if words[0].decode('utf-8') == IMAGE_NAME:
            old_image_id = words[2].decode('utf-8')
            break
    logger.info('Found it: {}'.format(old_image_id))
    logger.info('Done')
    # build new image
    cmd = 'docker build -t {} ./'.format(IMAGE_NAME)
    logger.info('Building image, name {}'.format(IMAGE_NAME))
    sp.run(cmd, shell=True, stdout=sp.PIPE, check=True)
    logger.info('Done')
    # remove old image
    cmd = 'docker rmi {}'.format(old_image_id)
    logger.info('Removing old image, id {}'.format(old_image_id))
    sp.run(cmd, shell=True, stdout=sp.PIPE, stderr=sp.PIPE)
    logger.info('Done')

def create_network():
    '''
    create the custom network, so that each node can communicate 
    with each other.
    Wouldn't throw error if it has already been created.

    Args:
        N/A
        
    Returns:
        N/A

    Raises:
        CalledProcessError
    '''
    cmd = 'docker network create {}'.format(NET_NAME)
    sp.run(cmd, shell=True, stderr=sp.PIPE, stdout=sp.PIPE, check=False)
    logger.info('Network created');

def run_node(names):
    '''
    create a docker container from my chord image

    Args:
        names: A list of node ids. The first one is id for this node.
                The second one is the node already in the ring.

    Returns:
        N/A

    Raises:
        CalledProcessError
    '''
    # hname = _hash(name)
    cname = CONTAINER_PREFIX + names[0]
    if len(names) == 1:
        cmd = 'docker run --name {} -dit --network={} {} {}'\
                .format(cname, NET_NAME, IMAGE_NAME, names[0])
    else:
        cmd = 'docker run --name {} -dit --network={} {} {} {}'\
                .format(cname, NET_NAME, IMAGE_NAME, names[0], names[1])
    logger.info('Starting container with name {}'.format(cname))
    sp.run(cmd, shell=True, stdout=sp.PIPE, check=True)
    logger.info('Done')

def clean_up(rm_img):
    '''
    clean up all the containers

    Args:
        rm_img: boolean to indicate whether to remove the image

    Returns:
        N/A

    Raises:
        CalledProcessError
    '''
    # find the containers using my chord image
    cmd = 'docker ps -a' 
    proc = sp.run(cmd, shell=True, stdout=sp.PIPE, check=True)
    lines = proc.stdout.splitlines()
    if len(lines) <= 1:
        logger.info('No containers found')
    else:
        for line in lines[1:]:
            container = line.split()[0].decode('utf-8')
            image = line.split()[1].decode('utf-8')
            if image == IMAGE_NAME:     # found and stop and rm
                cmd = 'docker stop {}'.format(container)
                logger.info('Stopping container {}'.format(container))
                sp.run(cmd, shell=True, stdout=sp.PIPE, check=True)
                logger.info('Done')
                cmd = 'docker rm {} -v'.format(container)
                logger.info('Removing ...')
                sp.run(cmd, shell=True, stdout=sp.PIPE, check=True)
                logger.info('done')
    # remove image if required
    if rm_img:
        cmd = 'docker rmi {}'.format(IMAGE_NAME)
        logger.info('Removing image {}'.format(IMAGE_NAME))
        sp.run(cmd, shell=True, stdout=sp.PIPE, check=True)
        logger.info('Done')

def local_finger_table():
    '''
    Send request to local node and get finger table information.

    Args:
        N/A

    Returns:
        N/A

    Raises:
        N/A
    '''
    r = requests.post('http://localhost:8000/display_finger_table', json={})
    assert(r.status_code==200)
    # format the output
    ft = r.json()['result']
    tbody = [[i, ft[i]] for i in range(1,len(ft))]
    print(tabulate.tabulate(tbody, headers=['Index', 'Node']))

def local_data():
    '''
    Display the key-value data of this node.

    Args:
        N/A

    Returns:
        N/A

    Raises:
        N/A
    '''
    r = requests.post('http://localhost:8000/display_data', json={})
    assert(r.status_code==200)
    # format the output
    data = r.json()['result']
    tbody = [[key, data[key]] for key in data]
    print(tabulate.tabulate(tbody, headers=['key', 'value']))
