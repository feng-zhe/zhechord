import subprocess as sp

IMAGE_NAME = 'fengzhe_chord'

def build_image():
    '''
    create the docker image for chord nodes

    Args:
        N/A
        
    Returns:
        N/A

    Raises:
        N/A
    '''
    cmd = 'docker build -t {} ./'.format(IMAGE_NAME)
    sp.run(cmd, shell=True, stdout=sp.PIPE, check=True)

def run_node(name):
    '''
    create a docker container from my chord image

    Args:
        name: any name for the node. It will be hashed and
            then used as the name for the container.

    Returns:
        N/A

    Raises:
        N/A
    '''
    cmd = 'docker run --name {} -dit {}'.format(name, IMAGE_NAME)
    sp.run(cmd, shell=True, stdout=sp.PIPE, check=True)

def clean_up(rm_img):
    '''
    clean up all the containers

    Args:
        rm_img: boolean to indicate whether to remove the image

    Returns:
        N/A

    Raises:
        N/A
    '''
    # find the containers using my chord image
    cmd = 'docker ps -a' 
    proc = sp.run(cmd, shell=True, stdout=sp.PIPE, check=True)
    lines = proc.stdout.splitlines()
    for line in lines[1:]:
        container = line.split()[0].decode('utf-8')
        image = line.split()[1].decode('utf-8')
        if image == IMAGE_NAME:     # found and stop and rm
            cmd = 'docker stop {}'.format(container)
            sp.run(cmd, shell=True, stdout=sp.PIPE, check=True)
            cmd = 'docker rm {} -v'.format(container)
            sp.run(cmd, shell=True, stdout=sp.PIPE, check=True)

