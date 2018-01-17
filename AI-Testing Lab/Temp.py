import datetime

def try_args(a, *rest):
    print(a)
    print()
    for x in rest:
        print(x)

if __name__ == '__main__':

    try_args(1,2,3,4,5)
