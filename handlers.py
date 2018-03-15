import hashlib
import subprocess as sp
import logging

logger = logging.getLogger(__name__)

IMAGE_NAME = 'fengzhe_chord'
NET_NAME = 'mynet'
RING_SIZE = 32

def _hash(name):
    '''
    Hash the name according to the RING_SIZE.

    Args:
        name:   a string to be hashed
        
    Returns:
        N/A

    Raises:
        N/A
    '''
    m = hashlib.sha1()
    m.update(name.encode('utf-8'))
    h = m.hexdigest()
    return h[:RING_SIZE//8]

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
    cmd = 'docker build -t {} ./'.format(IMAGE_NAME)
    logger.info('Build image, name {}'.format(IMAGE_NAME))
    sp.run(cmd, shell=True, stdout=sp.PIPE, check=True)
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

def run_node(name):
    '''
    create a docker container from my chord image

    Args:
        name: any name for the node. It will be hashed and
            then used as the name for the container.

    Returns:
        N/A

    Raises:
        CalledProcessError
    '''
    hname = _hash(name)
    cmd = 'docker run --name {} -dit --network={} {}'.format(hname, NET_NAME, IMAGE_NAME)
    logger.info('Starting container with hashed name {}'.format(hname))
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
