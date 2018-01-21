import datetime
import random


def try_del(dictA, BVal):
    if BVal in dictA:
        del dictA[BVal]


def reallywannatry(current_cell, destination_cell):
    if current_cell == destination_cell:
        return True

def getwhat(A, B):
    return [b for (b, a) in sorted(zip(B, A), key=lambda pair: pair[1])]

if __name__ == '__main__':
    A = ('move', 'me', (1,2,3), (2,3,4))
    B = ('move', 'me', (1,2,3), None)
    C = ('move', 'me', None, (2, 3, 4))
    D = ('move', None, (1, 2, 3), (2, 3, 4))
    E = (None, 'me', (1, 2, 3), (2, 3, 4))

    if None in A:
        print("A has None")

    if None in B:
        print("B has None")

    if None in C:
        print("C has None")

    if None in D:
        print("D has None")

    if None in E:
        print("E has None")
