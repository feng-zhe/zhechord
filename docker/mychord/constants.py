'''
Constants for the project.
'''

RING_SIZE_BIT = 160
ID_MAX = 2**160
TWO_EXP_TABLE = []  # the 2^i table

def init():
    if len(TWO_EXP_TABLE) == 0:
        for i in range(0, RING_SIZE_BIT+1):
            TWO_EXP_TABLE.append(2**i)

init()
