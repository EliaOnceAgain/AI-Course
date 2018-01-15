import datetime

def check_coordinate_within_grid_range(current_coordinate, grid_size):
    value = current_coordinate
    grid_legalization_part_1 = value < grid_size
    grid_legalization_part_2 = value >= 0
    return grid_legalization_part_1 and grid_legalization_part_2

if __name__ == '__main__':

    A = set()
    A.add('x')

    it = 1000

    dt1 = datetime.datetime.now()
    for _ in range(it):
        check_coordinate_within_grid_range(10, 50)
        check_coordinate_within_grid_range(10, 5)
    dt1 = datetime.datetime.now() - dt1

    # dt2 = datetime.datetime.now()
    # for _ in range(it):
    #     if 'x' not in A:
    #         A.add('x')
    # dt2 = datetime.datetime.now() - dt2

    print(dt1)
