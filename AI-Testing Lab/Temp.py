import datetime
import random


def try_del(dictA, BVal):
    if BVal in dictA:
        del dictA[BVal]


def reallywannatry(current_cell, destination_cell):
    if current_cell == destination_cell:
        return True


if __name__ == '__main__':
    A = [0, 0, 0, 0, 0, 0, 0, 0, 0, 0]
    B = [0, 0, 0, 0, 0, 0, 0, 0, 0, 0]

    max_A = [0, 0, 0, 0, 0, 0, 0, 0, 0, 0]
    max_B = [0, 0, 0, 0, 0, 0, 0, 0, 0, 0]

    AAA = range(10)

    for _ in range(100):
        for _ in range(20):
            sys_random_action = random.SystemRandom()
            random_action = sys_random_action.choice(AAA)
            A[random_action] += 1
            random_action = random.choice(AAA)
            B[random_action] += 1

        max_A[A.index(max(A))] += 1
        max_B[B.index(max(B))] += 1

    print(max_A)
    print()
    print(max_B)
