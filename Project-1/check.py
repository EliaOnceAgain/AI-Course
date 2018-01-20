import ex1
import ex11
import search
import time

# import networks

def timeout_exec(func, args=(), kwargs={}, timeout_duration=10, default=None):
    """This function will spawn a thread and run the given function
    using the args, kwargs and return the given default value if the
    timeout_duration is exceeded.
    """
    import threading
    class InterruptableThread(threading.Thread):
        def __init__(self):
            threading.Thread.__init__(self)
            self.result = default

        def run(self):
            # try:
            self.result = func(*args, **kwargs)
            # except Exception as e:
            #    self.result = (-3, -3, e)

    it = InterruptableThread()
    it.start()
    it.join(timeout_duration)
    if it.isAlive():
        return default
    else:
        return it.result


def check_problem(p, search_method, timeout):
    """ Constructs a problem using ex1.create_poisonserver_problem,
    and solves it using the given search_method with the given timeout.
    Returns a tuple of (solution length, solution time, solution)
    (-2, -2, None) means there was a timeout
    (-3, -3, ERR) means there was some error ERR during search"""

    t1 = time.time()
    s = timeout_exec(search_method, args=[p], timeout_duration=timeout)
    t2 = time.time()

    if isinstance(s, search.Node):
        solve = s
        solution = list(map(lambda n: n.action, solve.path()))[1:]
        return (len(solution), t2 - t1, solution)
    elif s is None:
        return (-2, -2, None)
    else:
        return s


def solve_problems(problems, goal, comparison_mode = False):
    solved = 0

    try:
        p = ex1.create_spaceship_problem(problems, goal)

    except Exception as e:
        print("Error creating problem: ", e)
        return None

    timeout = 60

    result = check_problem(p, (lambda p: search.best_first_graph_search(p, p.h)), timeout)

    print("GBFS ", result)
    if result[2] != None:
        if result[0] != -3:
            solved = solved + 1

    result = check_problem(p, search.astar_search, timeout)
    print("A*   ", result)

    ### --- BFS --- ###
    do_bfs = False
    if do_bfs:
        result = check_problem(p, search.breadth_first_search, timeout)
        print("BFS ", result)

    print("GBFS Solved ", solved)
    print("\n--------------------------------------\n")


def main():
    print(ex1.ids)
    print()

    # dimensions, list of ships, list of instruments, list of instruments on each ship,
    # calibration for each instrument, t
    # argets, ship starting locations

    # problem_id_to_run = list(range(7))
    # problem_id_to_run = list(range(9, ProblemsCount()))
    # problem_id_to_run = [-1]
    problem_id_to_run = [0]
    goal = None

    run_costums = 0
    if run_costums:
        print("Costum Problem 1")
        solve_problems(CostumProblem1(), goal)
        print("Costum Problem 2")
        solve_problems(CostumProblem2(), goal)

    number_of_runs = 1

    for _ in range(number_of_runs):
        if problem_id_to_run != None:
            for ind in problem_id_to_run:
                if ind < 0:
                    ind = ProblemsCount() + ind
                print("\n>> Running Problem " + str(ind))
                current_problem = AllProblems(ind)
                print("Problem Grid Size: ", current_problem[0])
                solve_problems(current_problem, goal, comparison_mode=True)

        print("------------------")

def CostumProblem1():
    # Stuck in corner with no movements
    return (3,
            ("sA", "sB"),
            ("d1",),
            {"sA": ("d1",), "sB": ("d1",)},
            {"d1": (0, 1, 0), "d2": (1, 1, 0), "d3": (1, 0, 0), "d4": (0, 0, 1)},
            {(0, 2, 2): ("d1",)},
            {"sA": (0, 0, 0), "sB": (1, 1, 2)}
            )


def CostumProblem2():
    # Stuck in corner with only one up movement
    return (3,
            ("sA", "sB"),
            ("d1",),
            {"sA": ("d1",), "sB": ("d1",)},
            {"d1": (0, 1, 0), "d2": (1, 1, 0), "d3": (1, 0, 0), "d4": (0, 0, 2), "d5": (0, 1, 1), "d6": (1, 1, 1),
             "d7": (1, 0, 1)},
            {(0, 2, 2): ("d1",)},
            {"sA": (0, 0, 0), "sB": (1, 1, 2)}
            )


def ProblemsDatabase():
    problems = []
    ##------------------- 0
    problems.append((5,
                     ("darth_vader", "wookie"),
                     ("rangefinder", "thermal_camera"),
                     {"darth_vader": ("rangefinder",), "wookie": ("thermal_camera", "rangefinder")},
                     {"rangefinder": (0, 3, 2), "thermal_camera": (1, 4, 2)},
                     {(1, 4, 1): ("thermal_camera", "rangefinder"), (4, 3, 4): ("thermal_camera", "rangefinder")},
                     {"darth_vader": (4, 1, 1), "wookie": (3, 0, 3)}
                     ))

    ##------------------- 1
    problems.append((4,
                     ('Rocinante', 'Yamato'),
                     ('alien life detector', 'reconnaissance USV', 'hyperspace probe'),
                     {'Yamato': ('alien life detector',), 'Rocinante': ('reconnaissance USV', 'hyperspace probe')},
                     {'alien life detector': (1, 1, 1), 'reconnaissance USV': (3, 2, 0), 'hyperspace probe': (1, 0, 2)},

                     {(0, 3, 3): ('alien life detector', 'hyperspace probe', 'reconnaissance USV'),
                      (2, 2, 1): ('alien life detector',), (0, 2, 1): ('reconnaissance USV', 'alien life detector'),
                      (0, 2, 3): ('reconnaissance USV', 'alien life detector'),
                      (2, 2, 0): ('alien life detector', 'hyperspace probe', 'reconnaissance USV'),
                      (2, 3, 0): ('alien life detector', 'reconnaissance USV', 'hyperspace probe'),
                      (1, 1, 0): ('hyperspace probe', 'reconnaissance USV', 'alien life detector')},

                     {'Rocinante': (0, 1, 1), 'Yamato': (1, 0, 1)},
                     ))

    ##------------------- 2
    problems.append((5,
                     ('Millennium Falcon', 'Galactica'),
                     ('D-EFT', 'wormhole detector', 'plasmoid camera'),
                     {'Galactica': ('D-EFT', 'wormhole detector'), 'Millennium Falcon': ('plasmoid camera',)},
                     {'D-EFT': (2, 2, 2), 'wormhole detector': (0, 0, 2), 'plasmoid camera': (4, 3, 0)},
                     {(1, 2, 0): ('plasmoid camera', 'wormhole detector'), (3, 1, 3): ('D-EFT',),
                      (2, 1, 4): ('D-EFT', 'wormhole detector'), (0, 4, 3): ('D-EFT', 'wormhole detector')},
                     {'Millennium Falcon': (1, 1, 4), 'Galactica': (1, 2, 4)},
                     ))

    ##------------------- 3
    problems.append((4,
                     ('Rocinante', 'Yamato'),
                     ('alien life detector', 'reconnaissance USV', 'hyperspace probe'),
                     {'Yamato': ('alien life detector',), 'Rocinante': ('reconnaissance USV', 'hyperspace probe')},
                     {'alien life detector': (1, 1, 1), 'reconnaissance USV': (3, 2, 0), 'hyperspace probe': (1, 0, 2)},
                     {(0, 3, 3): ('alien life detector', 'hyperspace probe', 'reconnaissance USV'),
                      (2, 2, 1): ('alien life detector',),
                      (0, 2, 1): ('reconnaissance USV', 'alien life detector'),
                      (0, 2, 3): ('reconnaissance USV', 'alien life detector'),
                      (2, 2, 0): ('alien life detector', 'hyperspace probe', 'reconnaissance USV'),
                      (2, 3, 0): ('alien life detector', 'reconnaissance USV', 'hyperspace probe'),
                      (1, 1, 0): ('hyperspace probe', 'reconnaissance USV', 'alien life detector')},
                     {'Rocinante': (0, 1, 1), 'Yamato': (1, 0, 1)}))

    ##------------------- 4
    problems.append((7,
                     ('Rocinante', 'Galactica', 'Yamato'),
                     ('spectrograph', 'tachyon cannon', 'wormhole detector', 'alien life detector'),
                     {'Yamato': ('spectrograph',), 'Galactica': ('tachyon cannon', 'wormhole detector'),
                      'Rocinante': ('alien life detector',)},
                     {'spectrograph': (1, 0, 6), 'tachyon cannon': (2, 4, 1), 'wormhole detector': (5, 6, 3),
                      'alien life detector': (6, 6, 1)},
                     {(5, 1, 4): ('alien life detector', 'wormhole detector', 'spectrograph'),
                      (3, 6, 4): ('wormhole detector',),
                      (0, 6, 5): ('tachyon cannon', 'spectrograph'), (1, 6, 0): ('alien life detector',),
                      (2, 2, 0): ('tachyon cannon',), (5, 0, 6): ('alien life detector', 'wormhole detector')},
                     {'Rocinante': (6, 0, 0), 'Galactica': (0, 5, 0), 'Yamato': (4, 5, 3)},
                     ))

    ##------------------- 5
    problems.append((5,
                     ('Sidonia', 'Galactica', 'Soyuz'),
                     ('alien life detector', 'QAS-2', 'D-EFT', 'X-ray scanner'),
                     {'Soyuz': ('alien life detector',), 'Sidonia': ('QAS-2',),
                      'Galactica': ('D-EFT', 'X-ray scanner')},
                     {'alien life detector': (0, 2, 1), 'QAS-2': (0, 2, 2), 'D-EFT': (4, 0, 2),
                      'X-ray scanner': (1, 1, 1)},
                     {(2, 3, 1): ('alien life detector', 'X-ray scanner', 'D-EFT'), (2, 0, 2): ('X-ray scanner',),
                      (1, 4, 4): ('alien life detector',), (2, 4, 4): ('QAS-2', 'alien life detector', 'D-EFT'),
                      (4, 0, 1): ('X-ray scanner',), (3, 1, 2): ('alien life detector',), (2, 1, 2): ('D-EFT',),
                      (3, 2, 3): ('D-EFT',),
                      (3, 2, 4): ('D-EFT', 'QAS-2', 'alien life detector'), (1, 0, 4): ('X-ray scanner',)},
                     {'Sidonia': (1, 2, 4), 'Galactica': (0, 0, 1), 'Soyuz': (3, 3, 0)},
                     ))

    ##------------------- 6
    problems.append((9,
                     ('Millennium Falcon', 'Rocinante', 'Apollo', 'Death Star'),
                     ('spectrograph', 'reconnaissance USV', 'plasmoid camera', 'hyperspace probe', 'X-ray scanner'),
                     {'Millennium Falcon': ('spectrograph',), 'Apollo': ('reconnaissance USV',),
                      'Death Star': ('plasmoid camera', 'hyperspace probe'), 'Rocinante': ('X-ray scanner',)},
                     {'spectrograph': (6, 4, 0), 'reconnaissance USV': (8, 2, 2), 'plasmoid camera': (0, 4, 4),
                      'hyperspace probe': (5, 5, 1), 'X-ray scanner': (2, 2, 5)},
                     {(1, 7, 6): ('X-ray scanner', 'spectrograph'), (7, 6, 5): ('spectrograph',),
                      (3, 3, 8): ('plasmoid camera',),
                      (1, 0, 2): ('plasmoid camera',),
                      (8, 6, 8): ('X-ray scanner', 'spectrograph', 'reconnaissance USV'),
                      (5, 1, 6): ('plasmoid camera', 'spectrograph', 'X-ray scanner'), (3, 4, 0): ('spectrograph',),
                      (3, 0, 1): ('plasmoid camera', 'reconnaissance USV')},
                     {'Millennium Falcon': (1, 5, 8), 'Rocinante': (0, 8, 4), 'Apollo': (0, 1, 7),
                      'Death Star': (7, 8, 6)},
                     ))

    ##------------------- 7
    problems.append((6,
                     ('Death Star', 'Apollo', 'Sidonia', 'Galactica'),
                     ('spectrograph', 'D-EFT', 'rangefinder', 'plasmoid camera', 'warp field meter'),
                     {'Death Star': ('spectrograph', 'D-EFT', 'rangefinder'),
                      'Apollo': ('plasmoid camera', 'warp field meter'),
                      'Sidonia': ('warp field meter',), 'Galactica': ('warp field meter',)},
                     {'spectrograph': (1, 3, 1), 'D-EFT': (2, 2, 2), 'rangefinder': (5, 5, 1),
                      'plasmoid camera': (0, 5, 2),
                      'warp field meter': (3, 3, 3)},
                     {(3, 3, 2): ('rangefinder',), (0, 4, 3): ('D-EFT', 'warp field meter', 'plasmoid camera'),
                      (1, 2, 5): ('rangefinder', 'D-EFT'), (4, 1, 4): ('warp field meter', 'D-EFT'),
                      (0, 1, 2): ('spectrograph',),
                      (5, 1, 0): ('plasmoid camera',), (4, 0, 5): ('rangefinder',),
                      (3, 2, 5): ('spectrograph', 'plasmoid camera', 'warp field meter'),
                      (0, 1, 3): ('D-EFT', 'warp field meter', 'rangefinder'), (2, 1, 0): ('warp field meter', 'D-EFT'),
                      (0, 0, 1): ('plasmoid camera', 'rangefinder'), (0, 5, 3): ('spectrograph',),
                      (1, 2, 1): ('rangefinder', 'D-EFT', 'spectrograph')},
                     {'Death Star': (2, 2, 1), 'Apollo': (4, 0, 3), 'Sidonia': (4, 4, 5), 'Galactica': (5, 5, 0)},
                     ))

    ##------------------- 8
    problems.append((11,
                     ('Death Star', 'Millennium Falcon', 'Yamato', 'Rama', 'Soyuz'),
                     (
                         'alien life detector', 'reconnaissance USV', 'wormhole detector', 'hyperspace probe',
                         'spectrograph',
                         'QAS-2'),
                     {'Millennium Falcon': ('alien life detector', 'reconnaissance USV'),
                      'Yamato': ('wormhole detector', 'hyperspace probe', 'spectrograph'), 'Death Star': ('QAS-2',),
                      'Rama': ('QAS-2',),
                      'Soyuz': ('reconnaissance USV',)},
                     {'alien life detector': (1, 3, 4), 'reconnaissance USV': (7, 2, 7), 'wormhole detector': (1, 7, 0),
                      'hyperspace probe': (5, 1, 7), 'spectrograph': (1, 0, 4), 'QAS-2': (10, 6, 2)},
                     {(9, 4, 8): ('reconnaissance USV', 'wormhole detector', 'hyperspace probe'),
                      (4, 7, 8): ('QAS-2', 'alien life detector'), (0, 9, 7): ('alien life detector', 'QAS-2'),
                      (4, 3, 3): ('alien life detector', 'QAS-2'), (5, 7, 10): ('spectrograph',), (1, 6, 6): ('QAS-2',),
                      (1, 0, 1): ('alien life detector',),
                      (5, 9, 2): ('reconnaissance USV', 'alien life detector', 'hyperspace probe'),
                      (3, 1, 5): ('reconnaissance USV', 'hyperspace probe'),
                      (0, 9, 5): ('wormhole detector', 'hyperspace probe')},
                     {'Death Star': (2, 8, 0), 'Millennium Falcon': (10, 8, 4), 'Yamato': (4, 4, 2), 'Rama': (2, 9, 5),
                      'Soyuz': (4, 10, 5)},
                     ))

    ##------------------- 9
    problems.append((7,
                     ('Yamato', 'Rama', 'Sidonia', 'Galactica', 'Millennium Falcon'),
                     ('hyperspace probe', 'X-ray scanner', 'alien life detector', 'spectrograph', 'QAS-2',
                      'tachyon cannon'),
                     {'Galactica': ('hyperspace probe', 'X-ray scanner', 'QAS-2'),
                      'Rama': ('alien life detector', 'tachyon cannon'),
                      'Sidonia': ('spectrograph',), 'Yamato': ('spectrograph',), 'Millennium Falcon': ('QAS-2',)},
                     {'hyperspace probe': (5, 1, 2), 'X-ray scanner': (2, 4, 4), 'alien life detector': (6, 3, 6),
                      'spectrograph': (5, 5, 6), 'QAS-2': (6, 3, 5), 'tachyon cannon': (4, 5, 5)},
                     {(4, 4, 3): ('alien life detector',), (5, 3, 5): ('alien life detector',),
                      (1, 3, 5): ('tachyon cannon', 'hyperspace probe', 'spectrograph'),
                      (6, 0, 1): ('hyperspace probe',),
                      (3, 6, 6): ('hyperspace probe', 'spectrograph', 'tachyon cannon'),
                      (1, 2, 4): ('spectrograph', 'alien life detector', 'tachyon cannon'),
                      (1, 6, 2): ('alien life detector',),
                      (5, 1, 6): ('spectrograph', 'tachyon cannon'),
                      (4, 6, 6): ('tachyon cannon', 'QAS-2', 'hyperspace probe'),
                      (3, 4, 0): ('hyperspace probe', 'X-ray scanner'),
                      (2, 0, 3): ('spectrograph', 'alien life detector'),
                      (0, 2, 6): ('hyperspace probe', 'X-ray scanner'), (2, 0, 4): ('tachyon cannon', 'X-ray scanner'),
                      (6, 3, 2): ('spectrograph', 'tachyon cannon'),
                      (1, 5, 4): ('hyperspace probe', 'alien life detector', 'QAS-2'),
                      (2, 3, 5): ('hyperspace probe', 'X-ray scanner')},
                     {'Yamato': (6, 5, 4), 'Rama': (1, 4, 0), 'Sidonia': (6, 4, 4), 'Galactica': (6, 3, 4),
                      'Millennium Falcon': (5, 5, 1)},
                     ))

    ##------------------- 10
    problems.append((13,
                     ('Apollo', 'Enterprise', 'Soyuz', 'Rocinante', 'Yamato', 'Galactica'),
                     ('D-EFT', 'X-ray scanner', 'rangefinder', 'reconnaissance USV', 'hyperspace probe',
                      'warp field meter',
                      'plasmoid camera'),
                     {'Soyuz': ('D-EFT', 'X-ray scanner', 'rangefinder', 'plasmoid camera'),
                      'Apollo': ('reconnaissance USV',),
                      'Enterprise': ('hyperspace probe', 'warp field meter'), 'Rocinante': ('plasmoid camera',),
                      'Yamato': ('reconnaissance USV',), 'Galactica': ('hyperspace probe',)},
                     {'D-EFT': (1, 3, 11), 'X-ray scanner': (4, 7, 0), 'rangefinder': (2, 4, 1),
                      'reconnaissance USV': (11, 2, 9),
                      'hyperspace probe': (6, 10, 11), 'warp field meter': (6, 1, 5), 'plasmoid camera': (11, 5, 4)},
                     {(10, 4, 0): ('hyperspace probe',), (12, 11, 1): ('D-EFT', 'X-ray scanner'),
                      (3, 11, 10): ('X-ray scanner', 'plasmoid camera', 'D-EFT'),
                      (9, 2, 11): ('plasmoid camera', 'reconnaissance USV'),
                      (10, 10, 12): ('rangefinder', 'warp field meter', 'plasmoid camera'),
                      (10, 5, 9): ('X-ray scanner',),
                      (9, 4, 6): ('X-ray scanner', 'D-EFT', 'rangefinder'),
                      (3, 0, 3): ('warp field meter', 'X-ray scanner', 'D-EFT'),
                      (2, 1, 4): ('rangefinder',),
                      (2, 7, 3): ('X-ray scanner', 'reconnaissance USV', 'hyperspace probe'),
                      (10, 4, 12): ('rangefinder',), (2, 12, 4): ('reconnaissance USV', 'warp field meter', 'D-EFT')},
                     {'Apollo': (8, 8, 11), 'Enterprise': (6, 12, 9), 'Soyuz': (3, 4, 2), 'Rocinante': (5, 7, 11),
                      'Yamato': (7, 10, 12), 'Galactica': (0, 10, 3)},
                     ))

    ##------------------- 11
    problems.append((8,
                     ('Yamato', 'Apollo', 'Galactica', 'Sidonia', 'Death Star', 'Soyuz'),
                     ('plasmoid camera', 'alien life detector', 'spectrograph', 'QAS-2', 'X-ray scanner', 'rangefinder',
                      'warp field meter'),
                     {'Yamato': ('plasmoid camera', 'alien life detector'), 'Apollo': ('spectrograph', 'rangefinder'),
                      'Sidonia': ('QAS-2', 'X-ray scanner'), 'Galactica': ('warp field meter',),
                      'Death Star': ('warp field meter',),
                      'Soyuz': ('rangefinder',)},
                     {'plasmoid camera': (7, 4, 0), 'alien life detector': (4, 5, 1), 'spectrograph': (6, 3, 0),
                      'QAS-2': (7, 5, 5),
                      'X-ray scanner': (6, 7, 4), 'rangefinder': (3, 7, 7), 'warp field meter': (6, 0, 0)},
                     {(5, 2, 0): ('rangefinder', 'alien life detector', 'plasmoid camera'),
                      (5, 6, 2): ('plasmoid camera',),
                      (7, 1, 7): ('alien life detector',),
                      (6, 3, 6): ('plasmoid camera', 'alien life detector', 'warp field meter'),
                      (4, 6, 5): ('plasmoid camera', 'warp field meter', 'rangefinder'),
                      (7, 3, 4): ('rangefinder', 'spectrograph', 'warp field meter'),
                      (7, 3, 1): ('plasmoid camera', 'rangefinder'),
                      (1, 5, 6): ('plasmoid camera', 'warp field meter', 'QAS-2'), (7, 2, 1): ('X-ray scanner',),
                      (4, 1, 2): ('alien life detector', 'QAS-2', 'rangefinder'),
                      (4, 6, 4): ('warp field meter', 'plasmoid camera', 'rangefinder'),
                      (3, 4, 4): ('spectrograph', 'warp field meter', 'X-ray scanner'),
                      (5, 3, 7): ('alien life detector', 'QAS-2', 'plasmoid camera'),
                      (3, 5, 4): ('alien life detector', 'plasmoid camera', 'spectrograph'),
                      (0, 0, 5): ('alien life detector',),
                      (6, 6, 1): ('warp field meter', 'spectrograph'), (3, 6, 0): ('rangefinder',),
                      (4, 1, 5): ('spectrograph', 'alien life detector'), (2, 1, 4): ('QAS-2', 'warp field meter')},
                     {'Yamato': (2, 7, 5), 'Apollo': (7, 7, 5), 'Galactica': (0, 2, 4), 'Sidonia': (5, 6, 6),
                      'Death Star': (2, 7, 1),
                      'Soyuz': (5, 3, 5)},
                     ))

    ##------------------- 12
    problems.append((15,
                     ('Death Star', 'Rama', 'Millennium Falcon', 'Enterprise', 'Yamato', 'Apollo', 'Galactica'),
                     (
                         'QAS-2', 'alien life detector', 'D-EFT', 'rangefinder', 'spectrograph', 'plasmoid camera',
                         'wormhole detector',
                         'reconnaissance USV'),
                     {'Rama': ('QAS-2', 'rangefinder'), 'Enterprise': ('alien life detector',),
                      'Apollo': ('D-EFT', 'plasmoid camera', 'reconnaissance USV'), 'Yamato': ('spectrograph',),
                      'Death Star': ('wormhole detector',), 'Millennium Falcon': ('rangefinder',),
                      'Galactica': ('D-EFT',)},
                     {'QAS-2': (0, 6, 5), 'alien life detector': (4, 2, 2), 'D-EFT': (14, 1, 0),
                      'rangefinder': (5, 13, 3),
                      'spectrograph': (0, 2, 14), 'plasmoid camera': (13, 10, 1), 'wormhole detector': (5, 1, 9),
                      'reconnaissance USV': (4, 11, 10)},
                     {(6, 12, 6): ('alien life detector', 'rangefinder'), (5, 6, 8): ('spectrograph',),
                      (13, 4, 4): ('QAS-2',),
                      (3, 0, 12): ('plasmoid camera',),
                      (10, 5, 14): ('rangefinder', 'alien life detector', 'spectrograph'),
                      (10, 6, 1): ('plasmoid camera',), (5, 0, 10): ('reconnaissance USV', 'plasmoid camera'),
                      (8, 11, 8): ('reconnaissance USV', 'alien life detector'),
                      (2, 10, 0): ('reconnaissance USV', 'wormhole detector', 'rangefinder'),
                      (11, 7, 11): ('wormhole detector', 'alien life detector', 'reconnaissance USV'),
                      (10, 4, 4): ('D-EFT', 'wormhole detector'), (1, 10, 0): ('QAS-2',),
                      (5, 2, 4): ('rangefinder', 'reconnaissance USV', 'alien life detector'),
                      (10, 6, 6): ('QAS-2', 'wormhole detector')},
                     {'Death Star': (1, 7, 8), 'Rama': (6, 5, 3), 'Millennium Falcon': (8, 13, 10),
                      'Enterprise': (4, 3, 3),
                      'Yamato': (7, 3, 8), 'Apollo': (11, 9, 6), 'Galactica': (6, 4, 3)},
                     ))

    ##------------------- 13
    problems.append((9,
                     ('Sidonia', 'Rocinante', 'Death Star', 'Yamato', 'Enterprise', 'Millennium Falcon', 'Apollo'),
                     ('rangefinder', 'tachyon cannon', 'alien life detector', 'reconnaissance USV', 'X-ray scanner',
                      'hyperspace probe',
                      'plasmoid camera', 'QAS-2'),
                     {'Sidonia': ('rangefinder', 'X-ray scanner', 'QAS-2'), 'Apollo': ('tachyon cannon',),
                      'Millennium Falcon': ('alien life detector', 'hyperspace probe'),
                      'Death Star': ('reconnaissance USV',),
                      'Enterprise': ('plasmoid camera',), 'Rocinante': ('QAS-2',), 'Yamato': ('QAS-2',)},
                     {'rangefinder': (8, 5, 1), 'tachyon cannon': (2, 0, 7), 'alien life detector': (7, 1, 5),
                      'reconnaissance USV': (6, 1, 3), 'X-ray scanner': (7, 0, 1), 'hyperspace probe': (0, 3, 0),
                      'plasmoid camera': (5, 3, 8), 'QAS-2': (2, 2, 5)},
                     {(4, 6, 8): ('plasmoid camera',), (5, 8, 8): ('alien life detector', 'rangefinder'),
                      (5, 2, 1): ('reconnaissance USV',), (8, 6, 0): ('plasmoid camera',),
                      (4, 6, 1): ('hyperspace probe',),
                      (0, 3, 6): ('rangefinder', 'X-ray scanner'),
                      (3, 2, 7): ('rangefinder', 'alien life detector', 'QAS-2'),
                      (5, 5, 5): ('hyperspace probe', 'tachyon cannon', 'alien life detector'),
                      (6, 5, 5): ('hyperspace probe', 'rangefinder', 'X-ray scanner'), (7, 5, 6): ('tachyon cannon',),
                      (2, 0, 1): ('alien life detector', 'QAS-2'), (8, 0, 7): ('rangefinder',),
                      (4, 8, 4): ('rangefinder', 'tachyon cannon'),
                      (0, 7, 2): ('tachyon cannon', 'plasmoid camera', 'reconnaissance USV'),
                      (0, 2, 5): ('rangefinder',),
                      (5, 1, 7): ('reconnaissance USV', 'alien life detector'),
                      (2, 6, 1): ('plasmoid camera', 'alien life detector'),
                      (4, 5, 4): ('plasmoid camera', 'QAS-2'), (3, 0, 4): ('QAS-2',),
                      (4, 6, 2): ('alien life detector', 'rangefinder'),
                      (5, 4, 6): ('QAS-2', 'plasmoid camera', 'tachyon cannon'),
                      (7, 5, 5): ('reconnaissance USV', 'QAS-2')},
                     {'Sidonia': (5, 3, 7), 'Rocinante': (8, 0, 3), 'Death Star': (6, 3, 6), 'Yamato': (4, 5, 3),
                      'Enterprise': (5, 2, 8), 'Millennium Falcon': (8, 8, 7), 'Apollo': (4, 3, 4)},
                     ))

    return problems


def AllProblems(problem_index):
    problems = ProblemsDatabase()
    return problems[problem_index]


def ProblemsCount():
    problems = ProblemsDatabase()
    return len(problems)


if __name__ == '__main__':
    main()
