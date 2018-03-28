'''
Constants for the project.
'''

CONTAINER_PREFIX = 'cr_'
RING_SIZE_BIT = 3
TWO_EXP = []  # the 2^i table, to speed up

def init():
    global TWO_EXP
    del TWO_EXP[:]
    for i in range(0, RING_SIZE_BIT+1):
        TWO_EXP.append(2**i)

init()