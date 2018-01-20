import datetime


def try_args(a, *rest):
    print(a)
    print()
    for x in rest:
        print(x)


def reallywannatry(current_cell, destination_cell):
    if current_cell == destination_cell:
        return True


if __name__ == '__main__':
    A, B, C = 1, 2, 3
    print(max(A,B,C))

