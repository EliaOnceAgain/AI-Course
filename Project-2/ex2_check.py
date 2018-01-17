import ex2_checker_client as ex2_checker


def get_num_of_transmitters(Lazer_transm_tuple):
    [x_y_trans, x_z_tran, y_z_tran] = Lazer_transm_tuple
    num_of_transmitters = len(x_y_trans) + len(x_z_tran) + len(y_z_tran)
    return num_of_transmitters


def test_checker():
    problems = []

    problem = (
        # dimensions, list of ships, list of instruments, list of instruments on each ship,
        # calibration for each instrument, targets, ship starting locations
        3,
        ("wookie",),
        ("rangefinder",),
        {"wookie": ("rangefinder",)},
        {"rangefinder": (0, 0, 2)},
        {(1, 2, 2): ("rangefinder",)},
        {"wookie": (0, 0, 0)}
    )
    # get the actual lazer locations represented by a 3 element tuple holding the 'x-y', 'x-z' and 'y-z' signals respectively
    lazer_locations = ((), (), ())
    problems.append([problem, lazer_locations, get_num_of_transmitters(lazer_locations)])

    lazer_locations = (((1, 0),), ((0, 1),), ((0, 1),))
    problems.append([problem, lazer_locations, get_num_of_transmitters(lazer_locations)])

    lazer_locations = (((1, 0),), (), ())
    problems.append([problem, lazer_locations, get_num_of_transmitters(lazer_locations)])

    lazer_locations = (((2, 1),), (), ())
    problems.append([problem, lazer_locations, get_num_of_transmitters(lazer_locations)])

    lazer_locations = (((1, 0),), ((1, 0),), ((1, 0),))
    problems.append([problem, lazer_locations, get_num_of_transmitters(lazer_locations)])

    lazer_locations = (((0, 1),), ((0, 1),), ((0, 1),))
    problems.append([problem, lazer_locations, get_num_of_transmitters(lazer_locations)])

    problem = (5,
               ('Soyuz', 'Death Star'),
               ('wormhole detector', 'hyperspace probe', 'D-EFT'),
               {'Soyuz': ('wormhole detector', 'D-EFT'), 'Death Star': ('hyperspace probe',)},
               {'wormhole detector': (1, 2, 3), 'hyperspace probe': (2, 0, 0), 'D-EFT': (1, 4, 3)},
               {(3, 4, 1): ('D-EFT', 'wormhole detector', 'hyperspace probe'),
                (1, 3, 1): ('wormhole detector', 'D-EFT', 'hyperspace probe'), (1, 2, 2): ('D-EFT',),
                (3, 3, 3): ('hyperspace probe', 'D-EFT', 'wormhole detector')},
               {'Soyuz': (1, 2, 1), 'Death Star': (0, 2, 4)},
               )

    # get the actual lazer locations represented by a 3 element tuple holding the 'x-y', 'x-z' and 'y-z' signals respectively
    lazer_locations = ((), (), ())
    problems.append([problem, lazer_locations, get_num_of_transmitters(lazer_locations)])

    lazer_locations = (((1, 0),), ((0, 1),), ((0, 1), (2, 2), (3, 1)))
    problems.append([problem, lazer_locations, get_num_of_transmitters(lazer_locations)])

    lazer_locations = (((1, 0), (4, 0)), ((4, 0)), ((3, 1)))
    problems.append([problem, lazer_locations, get_num_of_transmitters(lazer_locations)])

    for problem, lazer_locations, num_of_transmitters in problems:
        print('-----------------------------------------------------------')
        print('testing problem:')
        print(problem)
        print('lazer locations:')
        print(lazer_locations)
        print('-----------------')

        ex2_checker.check_solution(problem, lazer_locations)


if __name__ == '__main__':
    test_checker()
