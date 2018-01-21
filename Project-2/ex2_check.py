# import ex2_checker_client as ex2_checker
import ex2_checker_local as ex2_checker


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
    lazer_locations = ((), (), ())  # 0
    problems.append([problem, lazer_locations, get_num_of_transmitters(lazer_locations)])

    lazer_locations = (((1, 0),), ((0, 1),), ((0, 1),))  # 1
    problems.append([problem, lazer_locations, get_num_of_transmitters(lazer_locations)])

    lazer_locations = (((1, 0),), (), ())  # 2
    problems.append([problem, lazer_locations, get_num_of_transmitters(lazer_locations)])

    lazer_locations = (((2, 1),), (), ())  # 3
    problems.append([problem, lazer_locations, get_num_of_transmitters(lazer_locations)])

    lazer_locations = (((1, 0),), ((1, 0),), ((1, 0),))  # 4
    problems.append([problem, lazer_locations, get_num_of_transmitters(lazer_locations)])

    lazer_locations = (((0, 1),), ((0, 1),), ((0, 1),))  # 5
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
    lazer_locations = ((), (), ())  # 6
    problems.append([problem, lazer_locations, get_num_of_transmitters(lazer_locations)])

    lazer_locations = (((1, 0),), ((0, 1),), ((0, 1), (2, 2), (3, 1)))  # 7
    problems.append([problem, lazer_locations, get_num_of_transmitters(lazer_locations)])

    lazer_locations = (((1, 0), (4, 0)), ((4, 0),), ((3, 1),))  # 8
    problems.append([problem, lazer_locations, get_num_of_transmitters(lazer_locations)])

    number_of_runs = 10
    number_of_test_runs = 1
    result = None
    number_of_success = 0

    for i, p in enumerate(problems):
        problem, lazer_locations, num_of_transmitters = p
        print("Problem ID: ", i)

        win_ratio_all = 0
        for _ in range(number_of_test_runs):

            number_of_success = 0
            for _ in range(number_of_runs):
                result = ex2_checker.check_solution(problem, lazer_locations, print_single_results=False)
                #print()
                if result:
                    number_of_success += 1

            if number_of_test_runs == 1:
                print("Win Ratio: " + str(int((float(number_of_success) / float(number_of_runs)) * 100.0)) + "%")
            win_ratio_all += number_of_success / number_of_runs


        if number_of_test_runs > 1:
            print("Total Win Ratio: ", float(win_ratio_all) / float(number_of_test_runs))
        print()


        #print('####################################################\n')


if __name__ == '__main__':
    test_checker()
