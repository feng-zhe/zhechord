'''
Constants for the project.
'''

RING_SIZE_BIT = 160
ID_MAX = 2**RING_SIZE_BIT
TWO_EXP = []  # the 2^i table, to speed up

def init():
    ID_MAX = 2**RING_SIZE_BIT
    for i in range(0, RING_SIZE_BIT+1):
        TWO_EXP.append(2**i)

init()
