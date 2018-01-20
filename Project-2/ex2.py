__author__ = 'sarah'

ids = ["204657977"]

import logic
import search
import itertools
import functools
from copy import deepcopy

print_all_headlines = False
print_main_headlines = True


# ----------------------------------------------------------------------------------------------- #
# ------------------------------------- Small Problem World ------------------------------------- #
# ----------------------------------------------------------------------------------------------- #

class Problem(object):
    """The abstract class for a formal problem.  You should subclass
    this and implement the methods actions and result, and possibly
    __init__, goal_test, and path_cost. Then you will create instances
    of your subclass and solve them with the various search functions."""

    def __init__(self, initial, goal=None):
        """The constructor specifies the initial state, and possibly a goal
        state, if there is a unique goal.  Your subclass's constructor can add
        other arguments."""
        self.initial = initial
        self.goal = goal

    def actions(self, state):
        """Return the actions that can be executed in the given
        state. The result would typically be a list, but if there are
        many actions, consider yielding them one at a time in an
        iterator, rather than building them all at once."""
        raise NotImplementedError

    def result(self, state, action):
        """Return the state that results from executing the given
        action in the given state. The action must be one of
        self.actions(state)."""
        raise NotImplementedError

    def goal_test(self, state):
        """Return True if the state is a goal. The default method compares the
        state to self.goal or checks for state in self.goal if it is a
        list, as specified in the constructor. Override this method if
        checking against a single self.goal is not enough."""
        if isinstance(self.goal, list):
            return is_in(state, self.goal)
        else:
            return state == self.goal

    def path_cost(self, c, state1, action, state2):
        """Return the cost of a solution path that arrives at state2 from
        state1 via action, assuming cost c to get up to state1. If the problem
        is such that the path doesn't matter, this function will only look at
        state2.  If the path does matter, it will consider c and maybe state1
        and action. The default method costs 1 for every step in the path."""
        return c + 1

    def value(self, state):
        """For optimization problems, each state has a value.  Hill-climbing
        and related algorithms try to maximize this value."""
        raise NotImplementedError


class SmallProblemManager(Problem):
    def __init__(self, starting_coordinates, destination_coordinates, grid_manager, spaceship_dictionary):
        self.state = SmallProblem(starting_coordinates, destination_coordinates, grid_manager, spaceship_dictionary)
        Problem.__init__(self, initial=self.state)

    def actions(self, state):
        """Return the actions that can be executed in the given
        state. The result would typically be a tuple, but if there are
        many actions, consider yielding them one at a time in an
        iterator, rather than building them all at once."""
        all_possible_actions = state.get_possible_actions()
        for current_possible_action in all_possible_actions:
            yield current_possible_action

    def result(self, state, action):
        updated_state = deepcopy(state)
        updated_state.update_action(action)
        return updated_state

    def goal_test(self, state):
        return state.goal_test()

    def h(self, node):
        """ This is the heuristic. It gets a node (not a state,
        state can be accessed via node.state)
        and returns a goal distance estimate"""
        return node.state.current_heuristic()


class SmallProblem:
    def __init__(self, starting_coordinates, destination_coordinates, grid_manager, spaceship_dictionary, active_ship):
        self.starting_coordinates = starting_coordinates
        self.destination_coordinates = destination_coordinates
        self.current_coordinates = starting_coordinates

        self.grid_size = grid_manager.grid_obj.grid_size
        self.grid_manager = grid_manager

        self.active_ship = active_ship
        self.occupied_coordinates = set()
        self.spaceships_occupied_identifiers = set()
        self.spaceships_dictionary = spaceship_dictionary

    def add_target_occupied_coordinate(self, occupied_coordinate):
        self.occupied_coordinates.add(occupied_coordinate)

    def add_spaceship_occupied_coordinate(self, occupied_coordinate, occupied_identifier):
        self.occupied_coordinates.add(occupied_coordinate)
        self.spaceships_occupied_identifiers.add(occupied_identifier)

    def remove_spaceship_occupied_coordinate(self, occupied_coordinate, occupied_identifier):
        self.occupied_coordinates.remove(occupied_coordinate)
        self.spaceships_occupied_identifiers.remove(occupied_identifier)

    def get_action(self):
        distances, directions = UtilsGeneral.get_from_to_dist_dirc(self.current_coordinates,
                                                                   self.destination_coordinates)
        distances_directions = sorted(zip(distances, directions), key=lambda dist: dist[0])

        move_actions_set = set()
        for dist, dirc in distances_directions:
            new_coordinates = UtilsActions.new_coordinates_by_direction(self.current_coordinates, dirc)
            new_coordinates, _ = UtilsActions.coordinates_legalization(new_coordinates, self, self.grid_size,
                                                                       priority=False)
            if not self.grid_manager.check_action_destination_safety(new_coordinates):
                new_coordinates = None

            other_new_coordinates, other_spaceship_name = UtilsActions.coordinates_legalization(new_coordinates, self,
                                                                                                self.grid_size,
                                                                                                not_in_direction=dirc,
                                                                                                priority=True)
            if not self.grid_manager.check_action_destination_safety(other_new_coordinates):
                other_new_coordinates = None

            if new_coordinates:
                move_actions_set.add(("move", self.active_ship, self.current_coordinates, new_coordinates))
            if other_new_coordinates and other_spaceship_name:
                move_actions_set.add(("move", other_spaceship_name, new_coordinates, other_new_coordinates))

        return move_actions_set

    def update_action(self, action):
        UtilsUpdate.update_move_action(self.spaceships_dictionary[action[1]], action, self)
        self.current_coordinates = action[3]
        self.grid_manager.check_add_cell_spaceship(self.current_coordinates, action[1])

    def goal_test(self):
        if self.current_coordinates == self.destination_coordinates:
            return True
        return False

    def current_heuristic(self):
        return sum(abs(self.current_coordinates[0] - self.destination_coordinates[0]) +
                   abs(self.current_coordinates[1] - self.destination_coordinates[1]) +
                   abs(self.current_coordinates[2] - self.destination_coordinates[2]))

    def __hash__(self):
        return hash((frozenset(self.occupied_coordinates), frozenset(self.spaceships_occupied_identifiers)))

    def __eq__(self, other):
        return self.occupied_coordinates == other.occupied_coordinates \
               and self.spaceships_occupied_identifiers == other.spaceships_occupied_identifiers


def insort_right(a, x, lo=0, hi=None):
    """Insert item x in list a, and keep it sorted assuming a is sorted.

    If x is already in a, insert it to the right of the rightmost x.

    Optional args lo (default 0) and hi (default len(a)) bound the
    slice of a to be searched.
    """

    if lo < 0:
        raise ValueError('lo must be non-negative')
    if hi is None:
        hi = len(a)
    while lo < hi:
        mid = (lo + hi) // 2
        if x < a[mid]:
            hi = mid
        else:
            lo = mid + 1
    a.insert(lo, x)


def is_in(elt, seq):
    """Similar to (elt in seq), but compares with 'is', not '=='."""
    return any(x is elt for x in seq)


class Queue:
    """Queue is an abstract class/interface. There are three types:
        Stack(): A Last In First Out Queue.
        FIFOQueue(): A First In First Out Queue.
        PriorityQueue(order, f): Queue in sorted order (default min-first).
    Each type supports the following methods and functions:
        q.append(item)  -- add an item to the queue
        q.extend(items) -- equivalent to: for item in items: q.append(item)
        q.pop()         -- return the top item from the queue
        len(q)          -- number of items in q (also q.__len())
        item in q       -- does q contain item?
    Note that isinstance(Stack(), Queue) is false, because we implement stacks
    as lists.  If Python ever gets interfaces, Queue will be an interface."""

    def __init__(self):
        raise NotImplementedError

    def extend(self, items):
        for item in items:
            self.append(item)


class PriorityQueue(Queue):
    """A queue in which the minimum (or maximum) element (as determined by f and
    order) is returned first. If order is min, the item with minimum f(x) is
    returned first; if order is max, then it is the item with maximum f(x).
    Also supports dict-like lookup."""

    def __init__(self, order=min, f=lambda x: x):
        self.A = []
        self.order = order
        self.f = f

    def append(self, item):
        insort_right(self.A, (self.f(item), item))

    def __len__(self):
        return len(self.A)

    def pop(self):
        if self.order == min:
            return self.A.pop(0)[1]
        else:
            return self.A.pop()[1]

    def __contains__(self, item):
        return any(item == pair[1] for pair in self.A)

    def __getitem__(self, key):
        for _, item in self.A:
            if item == key:
                return item

    def __delitem__(self, key):
        for i, (value, item) in enumerate(self.A):
            if item == key:
                self.A.pop(i)


class Node:
    """A node in a search tree. Contains a pointer to the parent (the node
    that this is a successor of) and to the actual state for this node. Note
    that if a state is arrived at by two paths, then there are two nodes with
    the same state.  Also includes the action that got us to this state, and
    the total path_cost (also known as g) to reach the node.  Other functions
    may add an f and h value; see best_first_graph_search and astar_search for
    an explanation of how the f and h values are handled. You will not need to
    subclass this class."""

    def __init__(self, state, parent=None, action=None, path_cost=0):
        """Create a search tree Node, derived from a parent by an action."""
        self.state = state
        self.parent = parent
        self.action = action
        self.path_cost = path_cost
        self.depth = 0
        if parent:
            self.depth = parent.depth + 1

    def __repr__(self):
        return "<Node {}>".format(self.state)

    def __lt__(self, node):
        return self.state < node.state

    def expand(self, problem):
        """List the nodes reachable in one step from this node."""
        return [self.child_node(problem, action)
                for action in problem.actions(self.state)]

    def child_node(self, problem, action):
        """[Figure 3.10]"""
        next = problem.result(self.state, action)
        return Node(next, self, action,
                    problem.path_cost(self.path_cost, self.state,
                                      action, next))

    def solution(self):
        """Return the sequence of actions to go from the root to this node."""
        return [node.action for node in self.path()[1:]]

    def path(self):
        """Return a list of nodes forming the path from the root to this node."""
        node, path_back = self, []
        while node:
            path_back.append(node)
            node = node.parent
        return list(reversed(path_back))

    # We want for a queue of nodes in breadth_first_search or
    # astar_search to have no duplicated states, so we treat nodes
    # with the same state as equal. [Problem: this may not be what you
    # want in other contexts.]

    def __eq__(self, other):
        return isinstance(other, Node) and self.state == other.state

    def __hash__(self):
        return hash(self.state)


def memoize(fn, slot=None, maxsize=32):
    """Memoize fn: make it remember the computed value for any argument list.
    If slot is specified, store result in that slot of first argument.
    If slot is false, use lru_cache for caching the values."""
    if slot:
        def memoized_fn(obj, *args):
            if hasattr(obj, slot):
                return getattr(obj, slot)
            else:
                val = fn(obj, *args)
                setattr(obj, slot, val)
                return val
    else:
        @functools.lru_cache(maxsize=maxsize)
        def memoized_fn(*args):
            return fn(*args)

    return memoized_fn


def best_first_graph_search(problem, f):
    """Search the nodes with the lowest f scores first.
    You specify the function f(node) that you want to minimize; for example,
    if f is a heuristic estimate to the goal, then we have greedy best
    first search; if f is node.depth then we have breadth-first search.
    There is a subtlety: the line "f = memoize(f, 'f')" means that the f
    values will be cached on the nodes as they are computed. So after doing
    a best first search you can examine the f values of the path returned."""
    f = memoize(f, 'f')
    node = Node(problem.initialize)
    if problem.goal_test(node.state):
        return node
    frontier = PriorityQueue(min, f)
    frontier.append(node)
    explored = set()
    while frontier:
        node = frontier.pop()
        if problem.goal_test(node.state):
            return node
        explored.add(node.state)
        for child in node.expand(problem):
            if child.state not in explored and child not in frontier:

                frontier.append(child)
            elif child in frontier:
                incumbent = frontier[child]
                if f(child) < f(incumbent):
                    del frontier[incumbent]
                    frontier.append(child)

    return None

def astar_search(problem, h=None):
    """A* search is best-first graph search with f(n) = g(n)+h(n).
    You need to specify the h function when you call astar_search, or
    else in your Problem subclass."""
    h = memoize(h or problem.h, 'h')
    return best_first_graph_search(problem, lambda n: n.path_cost + h(n))

# ----------------------------------------------------------------------------------------------- #


class PriorityManager:
    def __init__(self, overview_obj):
        self.overview_obj = overview_obj
        self.device_spaceship_deadend = dict()
        self.dead_devices = set()

    def initialize_on_line_device(self):
        if print_all_headlines:
            print(">>> Function: initialize_on_line_device")

        self.overview_obj.is_turned_on = 0
        self.overview_obj.is_calibrated = 0
        self.overview_obj.calibration_current_estimate_index = 0
        self.overview_obj.use_device_current_estimate_index = 0

    def get_new_active_weapon(self):
        if print_all_headlines:
            print(">>> Function: get_new_active_weapon")

        for current_device in self.overview_obj.devices:
            if self.overview_obj.total_number_of_hits_per_device[current_device] != 0:
                self.overview_obj.online_device_id = self.overview_obj.devices.index(current_device)
                self.initialize_on_line_device()
                break

    def kill_device(self, current_device):
        if print_all_headlines:
            print(">>> Function: kill_device. Device to kill: " + str(current_device))
        self.overview_obj.dictionary_device_spaceships_priorities[current_device] = None
        self.overview_obj.dictionary_device_targets_priorities[current_device] = None
        self.dead_devices.add(current_device)

    def check_for_occlusions_calib(self, current_spaceship_coordinates, current_calibration_coordinates,
                                   distances_directions):
        if print_all_headlines:
            print(">>> Function: check_for_occlusions_calib")

        distances, directions = distances_directions

        found_occlusion = False
        occlusions_distances_set = set()

        for temp_target in self.overview_obj.targets_dict:
            temp_distance, temp_direction, is_target_straight = UtilsActions.check_straight_line(
                current_spaceship_coordinates, temp_target)
            if is_target_straight:
                if temp_direction == directions:
                    if temp_distance < distances:
                        found_occlusion = True
                        occlusions_distances_set.add(temp_distance)

        for temp_calib in self.overview_obj.calibration_targets_dict.values():
            if temp_calib != current_calibration_coordinates:
                temp_distance, temp_direction, is_target_straight = UtilsActions.check_straight_line(
                    current_spaceship_coordinates, temp_calib)
                if is_target_straight:
                    if temp_direction == directions:
                        if temp_distance < distances:
                            found_occlusion = True
                            occlusions_distances_set.add(temp_distance)

        return found_occlusion, occlusions_distances_set

    def check_for_occlusions_target(self, current_spaceship_coordinates, current_target_coordinates,
                                    distances_directions):
        if print_all_headlines:
            print(">>> Function: check_for_occlusions_target")

        distances, directions = distances_directions

        found_occlusion = False
        occlusions_distances_set = set()

        for temp_target in self.overview_obj.targets_dict:
            if temp_target != current_target_coordinates:
                temp_distance, temp_direction, is_target_straight = UtilsActions.check_straight_line(
                    current_spaceship_coordinates, temp_target)
                if is_target_straight:
                    if temp_direction == directions:
                        if temp_distance < distances:
                            found_occlusion = True
                            occlusions_distances_set.add(temp_distance)

        for temp_calib in self.overview_obj.calibration_targets_dict.values():
            temp_distance, temp_direction, is_target_straight = UtilsActions.check_straight_line(
                current_spaceship_coordinates, temp_calib)
            if is_target_straight:
                if temp_direction == directions:
                    if temp_distance < distances:
                        found_occlusion = True
                        occlusions_distances_set.add(temp_distance)

        return found_occlusion, occlusions_distances_set

    def add_priority_to_sorted_list_calib(self, current_spaceship, current_device, priority_value,
                                          distances_directions):
        for i_index in range(len(self.overview_obj.dictionary_device_spaceships_priorities[current_device])):
            if priority_value < \
                    self.overview_obj.dictionary_device_spaceships_priorities[current_device][i_index][1]:
                self.overview_obj.dictionary_device_spaceships_priorities[current_device].insert(i_index,
                                                                                                 [current_spaceship,
                                                                                                  priority_value,
                                                                                                  distances_directions])
                break
        else:
            self.overview_obj.dictionary_device_spaceships_priorities[current_device].append(
                [current_spaceship, priority_value, distances_directions])

    def add_priority_to_sorted_list_target(self, current_target_coordinates, current_device, priority_value,
                                           distances_directions):
        for i_index in range(len(self.overview_obj.dictionary_device_targets_priorities[current_device])):
            if priority_value < \
                    self.overview_obj.dictionary_device_targets_priorities[current_device][i_index][1]:
                self.overview_obj.dictionary_device_targets_priorities[current_device].insert(i_index,
                                                                                              [
                                                                                                  current_target_coordinates,
                                                                                                  priority_value,
                                                                                                  distances_directions])
                break
        else:
            self.overview_obj.dictionary_device_targets_priorities[current_device].append(
                [current_target_coordinates, priority_value, distances_directions])

    def get_straight_priority_order(self, target_distance, occlusions_distances_set):
        number_of_occlusions = len(occlusions_distances_set)
        min_distance = min(occlusions_distances_set)
        max_distance = max(occlusions_distances_set)

        if number_of_occlusions == 1:
            if max_distance == target_distance - 1:
                return min_distance + 3
            else:
                return min_distance + 4
        else:
            return min_distance - 1 + number_of_occlusions * 3

    def add_device_ship_deadend(self, device_name, ship_name):
        if device_name in self.device_spaceship_deadend:
            if ship_name not in self.device_spaceship_deadend[device_name]:
                self.device_spaceship_deadend[device_name].append(ship_name)
        else:
            self.device_spaceship_deadend[device_name] = [ship_name]


class CalibPriorityManager(PriorityManager):
    def __init__(self, overview_obj):
        super().__init__(overview_obj)

    def pass_device_checks(self, current_device):
        # current_device - Current Device Name (string)
        if self.overview_obj.total_number_of_hits_per_device[current_device] != 0:
            return True

        else:
            self.kill_device(current_device)
            return False

    def pass_spaceship_checks(self, current_device, current_spaceship):
        if current_spaceship.check_device_exists(current_device):
            if current_device in self.device_spaceship_deadend:
                if current_spaceship.name in self.device_spaceship_deadend[current_device]:
                    return False
            return True
        return False

    def get_current_calib_priority(self, current_spaceship, device_calibration_coordinates, all_distances_dict):
        if print_all_headlines:
            print(">>> Function: get_current_calib_priority")

        current_spaceship_coordinates = current_spaceship.coordinates
        distances, directions, is_straight_line = all_distances_dict[
            (current_spaceship_coordinates, device_calibration_coordinates)]

        if is_straight_line:
            found_occlusion, occlusions_distances_set = self.check_for_occlusions_calib(
                current_spaceship_coordinates, device_calibration_coordinates, (distances, directions))

            if not found_occlusion:
                priority_value = 0
            else:
                priority_value = self.get_straight_priority_order(distances, occlusions_distances_set)

            return [current_spaceship, priority_value, (distances, directions)]

        else:
            priority_value = sum(distances) - max(distances)
            distances_directions = sorted(zip(distances, directions), key=lambda dist: dist[0])
            return [current_spaceship, priority_value, distances_directions]

    def priority_calib_main(self):
        if print_all_headlines or print_main_headlines:
            print(">>> Function: priority_calib_main")

        def get_current_device_data(current_device):
            if self.pass_device_checks(current_device):
                temporary_priorities = []
                device_calibration_coordinates = self.overview_obj.calibration_targets_dict[current_device]

                for current_spaceship in self.overview_obj.spaceships.values():
                    if self.pass_spaceship_checks(current_device, current_spaceship):
                        current_priority = self.get_current_calib_priority(current_spaceship,
                                                                           device_calibration_coordinates,
                                                                           all_distances_dict)

                        temporary_priorities.append(current_priority)

                        # if current_priority[1] == 0:
                        #     temporary_priorities.insert(0, current_priority)
                        #     self.overview_obj.dictionary_device_spaceships_priorities[
                        #         current_device] = temporary_priorities
                        #     return True
                        #
                        # else:
                        #     temporary_priorities.append(current_priority)

                if len(temporary_priorities) > 0:
                    temporary_priorities.sort(key=lambda priority: priority[1])
                    self.overview_obj.dictionary_device_spaceships_priorities[current_device] = temporary_priorities
                    return True

            return False

        all_distances_dict = UtilsGeneral.get_all_distances_dict(self.overview_obj.spaceships,
                                                                 self.overview_obj.targets_dict,
                                                                 self.overview_obj.calibration_targets_dict)

        for current_device in self.overview_obj.devices:
            if current_device not in self.dead_devices:
                if get_current_device_data(current_device):
                    self.reset_introduced_device(current_device)
                    break

        self.get_new_active_weapon()

    def priority_calib_update(self):
        if print_all_headlines or print_main_headlines:
            print(">>> Function: priority_calib_update")

        current_device = self.overview_obj.devices[self.overview_obj.online_device_id]
        current_estimate = self.overview_obj.dictionary_device_spaceships_priorities[current_device][
            self.overview_obj.calibration_current_estimate_index]
        current_estimate_spaceship = current_estimate[0]
        current_spaceship_coordinates = current_estimate_spaceship.coordinates
        device_calibration_coordinates = self.overview_obj.calibration_targets_dict[current_device]

        distances, directions, is_straight_line = UtilsActions.check_straight_line(
            current_spaceship_coordinates, device_calibration_coordinates)

        if is_straight_line:
            found_occlusion, occlusions_distances_set = self.check_for_occlusions_calib(
                current_spaceship_coordinates, device_calibration_coordinates, (distances, directions))

            if not found_occlusion:
                priority_value = 0

            else:
                priority_value = self.get_straight_priority_order(distances, occlusions_distances_set)

            self.overview_obj.dictionary_device_spaceships_priorities[current_device][
                self.overview_obj.calibration_current_estimate_index] = [
                current_estimate_spaceship, priority_value, (distances, directions)]

        else:
            priority_value = sum(distances) - max(distances)
            distances_directions = sorted(zip(distances, directions), key=lambda dist: dist[0])

            self.overview_obj.dictionary_device_spaceships_priorities[current_device][
                self.overview_obj.calibration_current_estimate_index] = [
                current_estimate_spaceship, priority_value, distances_directions]

    def get_calib_estimate_action(self, current_estimate, current_device, as_single=False):
        current_estimate_spaceship = current_estimate[0]
        current_estimate_spaceship_name = current_estimate_spaceship.name

        if current_estimate[1] == 0:
            if current_estimate_spaceship.check_ready_calibrate(current_device):
                if as_single:
                    return ('calibrate', current_estimate_spaceship_name, current_device,
                            self.overview_obj.calibration_targets_dict[current_device])
                else:
                    return (('calibrate', current_estimate_spaceship_name, current_device,
                             self.overview_obj.calibration_targets_dict[current_device]),)
            else:
                if as_single:
                    return ('turn_on', current_estimate_spaceship_name, current_device)
                else:
                    return (('turn_on', current_estimate_spaceship_name, current_device),)
        else:
            return UtilsActions.get_move_action_priority_calibration(current_estimate, self.overview_obj.state,
                                                                     self.overview_obj.grid_size)

    def get_calibration_actions(self, grid_manager):
        if print_all_headlines or print_main_headlines:
            print(">>> Function: get_calibration_actions")

        current_device = self.overview_obj.devices[self.overview_obj.online_device_id]

        current_estimate = self.overview_obj.dictionary_device_spaceships_priorities[current_device][
            self.overview_obj.calibration_current_estimate_index]

        if current_estimate[1] == 0:
            return self.get_calib_estimate_action(current_estimate, current_device, as_single=True)

        for current_estimate_index in range(
                len(self.overview_obj.dictionary_device_spaceships_priorities[current_device])):

            current_estimate = self.overview_obj.dictionary_device_spaceships_priorities[current_device][
                current_estimate_index]
            current_estimate_actions_set = self.get_calib_estimate_action(current_estimate, current_device)

            self.overview_obj.calibration_current_estimate_index = current_estimate_index
            for current_action in current_estimate_actions_set:
                yield current_action

            self.add_device_ship_deadend(current_device, current_estimate[0].name)


class TargetPriorityManager(PriorityManager):
    def __init__(self, overview_obj):
        super().__init__(overview_obj)
        self.devices_introduced = set()

    def reset_introduced_device(self, current_device):
        if current_device in self.devices_introduced:
            self.devices_introduced.remove(current_device)

    def priority_target_update(self):
        if print_all_headlines or print_main_headlines:
            print(">>> Function: priority_target_update")

        current_device = self.overview_obj.devices[self.overview_obj.online_device_id]
        current_estimate_spaceship = self.overview_obj.dictionary_device_spaceships_priorities[current_device][
            self.overview_obj.calibration_current_estimate_index][0]
        current_spaceship_coordinates = current_estimate_spaceship.coordinates
        current_target_coordinates = self.overview_obj.dictionary_device_targets_priorities[current_device][
            self.overview_obj.use_device_current_estimate_index][0]

        distances, directions, is_straight_line = UtilsActions.check_straight_line(
            current_spaceship_coordinates, current_target_coordinates)

        if is_straight_line:
            found_occlusion, occlusions_distances_set = self.check_for_occlusions_calib(
                current_spaceship_coordinates, current_target_coordinates, (distances, directions))

            if not found_occlusion:
                priority_value = 0
            else:
                priority_value = self.get_straight_priority_order(distances, occlusions_distances_set)

            self.overview_obj.dictionary_device_targets_priorities[current_device][
                self.overview_obj.use_device_current_estimate_index] = [
                current_target_coordinates, priority_value, (distances, directions)]

        else:
            priority_value = sum(distances) - max(distances)
            distances_directions = sorted(zip(distances, directions), key=lambda dist: dist[0])

            self.overview_obj.dictionary_device_targets_priorities[current_device][
                self.overview_obj.use_device_current_estimate_index] = [
                current_target_coordinates, priority_value,
                distances_directions]

    def priority_target_main(self):
        if print_all_headlines or print_main_headlines:
            print(">>> Function: priority_target_main")

        current_device = self.overview_obj.devices[self.overview_obj.online_device_id]
        current_estimate = self.overview_obj.dictionary_device_spaceships_priorities[current_device][
            self.overview_obj.calibration_current_estimate_index]
        current_estimate_spaceship = current_estimate[0]
        current_spaceship_coordinates = current_estimate_spaceship.coordinates

        all_distances_dict = UtilsGeneral.get_all_distances_dict(self.overview_obj.spaceships,
                                                                 self.overview_obj.targets_dict,
                                                                 self.overview_obj.calibration_targets_dict,
                                                                 specific_spaceship=current_estimate_spaceship)

        found_zero_priority = False
        temporary_priorities = []
        for current_target in self.overview_obj.targets_dict:
            if current_device in self.overview_obj.targets_dict[current_target]:
                current_priority = self.get_current_target_priority(current_spaceship_coordinates, current_target,
                                                                    all_distances_dict)
                if current_priority[1] == 0:
                    temporary_priorities.insert(0, current_priority)
                    self.overview_obj.dictionary_device_targets_priorities[current_device] = temporary_priorities
                    self.reset_introduced_device(current_device)
                    found_zero_priority = True
                    break
                else:
                    temporary_priorities.append(current_priority)

        if not found_zero_priority:
            temporary_priorities.sort(key=lambda priority: priority[1])
            self.overview_obj.dictionary_device_targets_priorities[current_device] = temporary_priorities
            self.reset_introduced_device(current_device)

    def get_current_target_priority(self, current_spaceship_coordinates, current_target_coordinates,
                                    all_distances_dict):
        if print_all_headlines:
            print(">>> Function: get_current_target_priority")

        distances, directions, is_straight_line = all_distances_dict[
            (current_spaceship_coordinates, current_target_coordinates)]

        if is_straight_line:
            found_occlusion, occlusions_distances_set = self.check_for_occlusions_target(
                current_spaceship_coordinates, current_target_coordinates, (distances, directions))

            if not found_occlusion:
                priority_value = 0
            else:
                priority_value = self.get_straight_priority_order(distances, occlusions_distances_set)

            return [current_target_coordinates, priority_value, (distances, directions)]

        else:
            priority_value = sum(distances) - max(distances)
            distances_directions = sorted(zip(distances, directions), key=lambda dist: dist[0])
            return [current_target_coordinates, priority_value, distances_directions]

    def get_target_actions(self):
        if print_all_headlines or print_main_headlines:
            print(">>> Function: get_target_actions")

        def introduce_device(current_device):
            if current_device in self.devices_introduced:
                return False
            return True

        current_device = self.overview_obj.devices[self.overview_obj.online_device_id]
        current_device_calib_estimate = self.overview_obj.dictionary_device_spaceships_priorities[current_device][
            self.overview_obj.calibration_current_estimate_index]
        current_estimate_spaceship = current_device_calib_estimate[0]
        current_estimate_spaceship_name = current_estimate_spaceship.name

        current_use_estimate = self.overview_obj.dictionary_device_targets_priorities[current_device][
            self.overview_obj.use_device_current_estimate_index]

        current_use_estimate_target_coordinates = current_use_estimate[0]

        if current_use_estimate[1] == 0:
            yield ('use', current_estimate_spaceship_name, current_device, current_use_estimate_target_coordinates)

        elif introduce_device(current_device):
            self.devices_introduced.add(current_device)
            for current_estimate_index in range(
                    len(self.overview_obj.dictionary_device_targets_priorities[current_device])):

                current_estimate = self.overview_obj.dictionary_device_targets_priorities[current_device][
                    current_estimate_index]

                current_estimate_actions_set = UtilsActions.get_move_action_priority_targets(current_estimate,
                                                                                             current_estimate_spaceship,
                                                                                             self.overview_obj.state,
                                                                                             self.overview_obj.grid_size)

                self.overview_obj.use_device_current_estimate_index = current_estimate_index
                for current_action in current_estimate_actions_set:
                    yield current_action

            # Make sure 'use_device_current_estimate_index' is initialized to zero somewhere in Calib priority
            self.overview_obj.calib_priority_manager.add_device_ship_deadend(current_device,
                                                                             current_estimate_spaceship_name)
            self.overview_obj.calib_priority_manager.priority_calib_main()
            calibration_actions = self.overview_obj.calib_priority_manager.get_calibration_actions()
            for current_action in calibration_actions:
                yield current_action


        else:
            current_estimate = self.overview_obj.dictionary_device_targets_priorities[current_device][
                self.overview_obj.use_device_current_estimate_index]
            current_estimate_actions_set = UtilsActions.get_move_action_priority_targets(current_estimate,
                                                                                         current_estimate_spaceship,
                                                                                         self.overview_obj.state,
                                                                                         self.overview_obj.grid_size)

            for current_action in current_estimate_actions_set:
                yield current_action


class UtilsGeneral:
    @staticmethod
    def get_all_distances_dict(spaceships, targets_dict, calibration_targets_dict, specific_spaceship=None):
        all_distances_dict = dict()

        if not specific_spaceship:
            for current_spaceship in spaceships.values():
                current_spaceship_coordinates = current_spaceship.coordinates

                for current_target_coordinates in targets_dict:
                    temp_distance, temp_direction, is_straight_line = UtilsActions.check_straight_line(
                        current_spaceship_coordinates, current_target_coordinates)
                    all_distances_dict[(current_spaceship_coordinates, current_target_coordinates)] = [
                        temp_distance, temp_direction, is_straight_line]

                for temp_calib_coordinates in calibration_targets_dict.values():
                    temp_distance, temp_direction, is_straight_line = UtilsActions.check_straight_line(
                        current_spaceship_coordinates, temp_calib_coordinates)
                    all_distances_dict[(current_spaceship_coordinates, temp_calib_coordinates)] = [
                        temp_distance, temp_direction, is_straight_line]

        else:
            current_spaceship_coordinates = specific_spaceship.coordinates

            for current_target_coordinates in targets_dict:
                temp_distance, temp_direction, is_straight_line = UtilsActions.check_straight_line(
                    current_spaceship_coordinates, current_target_coordinates)
                all_distances_dict[(current_spaceship_coordinates, current_target_coordinates)] = [
                    temp_distance, temp_direction, is_straight_line]

            for temp_calib_coordinates in calibration_targets_dict.values():
                temp_distance, temp_direction, is_straight_line = UtilsActions.check_straight_line(
                    current_spaceship_coordinates, temp_calib_coordinates)
                all_distances_dict[(current_spaceship_coordinates, temp_calib_coordinates)] = [
                    temp_distance, temp_direction, is_straight_line]

        return all_distances_dict

    @staticmethod
    def get_from_to_dist_dirc(tuple_coordinate1, tuple_coordinate2):

        dx = tuple_coordinate2[0] - tuple_coordinate1[0]
        dy = tuple_coordinate2[1] - tuple_coordinate1[1]
        dz = tuple_coordinate2[2] - tuple_coordinate1[2]

        distances_to_return = []
        directions_to_return = []

        if dx:
            if dx > 0:
                distances_to_return.append(dx)
                directions_to_return.append('dx')
            else:
                distances_to_return.append(-dx)
                directions_to_return.append('-dx')

        if dy:
            if dy > 0:
                distances_to_return.append(dy)
                directions_to_return.append('dy')
            else:
                distances_to_return.append(-dy)
                directions_to_return.append('-dy')

        if dz:
            if dz > 0:
                distances_to_return.append(dz)
                directions_to_return.append('dz')
            else:
                distances_to_return.append(-dz)
                directions_to_return.append('-dz')

        return distances_to_return, directions_to_return


class UtilsUpdate:
    @staticmethod
    def distribute_packet(action, spaceships_dictionary, targets_dictionary, state):
        if print_all_headlines:
            print(">>> Function: distribute_packet")
        if action[0] == 'move':
            UtilsUpdate.update_move_action(spaceships_dictionary[action[1]], action, state)
        elif action[0] == 'turn_on':
            UtilsUpdate.update_turnon_action(spaceships_dictionary[action[1]], action, state)
        elif action[0] == 'calibrate':
            UtilsUpdate.update_calibrate_action(spaceships_dictionary[action[1]], action, state)
        else:  # elif action[0] == 'use':
            UtilsUpdate.update_use_action(spaceships_dictionary[action[1]], action, targets_dictionary, state)

    @staticmethod
    def update_move_action(spaceship_object, move_action, state):
        if print_all_headlines:
            print(">>> Function: update_move_action")
        spaceship_old_coordinates = spaceship_object.coordinates
        spaceship_old_identifier = spaceship_object.get_spaceship_identifier()
        state.remove_spaceship_occupied_coordinate(spaceship_old_coordinates, spaceship_old_identifier)
        spaceship_object.coordinates = move_action[3]
        state.add_spaceship_occupied_coordinate(spaceship_object.coordinates,
                                                spaceship_object.get_spaceship_identifier())

    @staticmethod
    def update_turnon_action(spaceship_object, turnon_action, state):
        if print_all_headlines:
            print(">>> Function: update_turnon_action")
        value_to_remove = spaceship_object.turn_off_devices()
        value_to_add = spaceship_object.turn_on_device(turnon_action[2])
        if value_to_remove:
            state.remove_device_status(value_to_remove)
        state.add_device_status(value_to_add)

    @staticmethod
    def update_calibrate_action(spaceship_object, calibrate_action, state):
        if print_all_headlines:
            print(">>> Function: update_calibrate_action")
        value_to_remove, value_to_add = spaceship_object.calibrate_device(calibrate_action[2])
        if value_to_remove:
            state.remove_device_status(value_to_remove)
        state.add_device_status(value_to_add)

    @staticmethod
    def update_use_action(spaceship_object, use_action, targets_dictionary, state):
        if print_all_headlines:
            print(">>> Function: update_use_action")
        current_device = use_action[2]
        current_target = use_action[3]
        targets_dictionary[current_target] = tuple(
            device for device in targets_dictionary[current_target] if device != current_device)
        state.add_target_hit((current_target, current_device))


class UtilsActions:
    @staticmethod
    def good_cop_bad_cop(current_name, current_coordinates, state, grid_size, distances_directions):
        if print_all_headlines:
            print(">>> Function: good_cop_bad_cop")

        temp_move_actions_set = set()
        for dist, dirc in distances_directions:
            new_coordinates = UtilsActions.new_coordinates_by_direction(current_coordinates, dirc)

            new_coordinates_easy_check, _ = UtilsActions.coordinates_legalization(new_coordinates, state, grid_size,
                                                                                  priority=False)

            other_new_coordinates = None
            other_spaceship_name = None
            if not new_coordinates_easy_check:
                other_new_coordinates, other_spaceship_name = UtilsActions.coordinates_legalization(new_coordinates,
                                                                                                    state,
                                                                                                    grid_size,
                                                                                                    not_in_direction=[
                                                                                                        dirc],
                                                                                                    priority=True)

            if new_coordinates_easy_check:
                temp_move_actions_set.add(("move", current_name, current_coordinates, new_coordinates_easy_check))
            if other_new_coordinates and other_spaceship_name:
                temp_move_actions_set.add(("move", other_spaceship_name, new_coordinates, other_new_coordinates))

        return temp_move_actions_set

    @staticmethod
    def get_move_action_priority_calibration(current_estimate, state, grid_size):
        if print_all_headlines:
            print(">>> Function: get_move_action_priority_calibration")

        current_ship_name = current_estimate[0].name
        current_ship_coordinates = current_estimate[0].coordinates
        distances_directions = current_estimate[2]

        if isinstance(distances_directions[0], int):
            distances_directions = (distances_directions,)

        move_actions_set = UtilsActions.good_cop_bad_cop(current_ship_name, current_ship_coordinates, state, grid_size,
                                                         distances_directions)

        return move_actions_set

    @staticmethod
    def get_move_action_priority_targets(current_estimate, current_spaceship, state, grid_size):
        if print_all_headlines:
            print(">>> Function: get_move_action_priority_targets")

        move_actions_set = set()
        current_ship_name = current_spaceship.name
        current_ship_coordinates = current_spaceship.coordinates
        distances_directions = current_estimate[2]

        if isinstance(distances_directions[0], int):
            distances_directions = (distances_directions,)

        move_actions_set.update(
            UtilsActions.good_cop_bad_cop(current_ship_name, current_ship_coordinates, state, grid_size,
                                          distances_directions))

        return move_actions_set

    @staticmethod
    def coordinates_legalization(current_coordinates, state, grid_size, not_in_direction=None, priority=True):
        if print_all_headlines:
            print(">>> Function: coordinates_legalization")

        if UtilsActions.check_within_grid_range(current_coordinates, grid_size):
            if current_coordinates not in state.occupied_coordinates:
                return (current_coordinates, None)
            elif priority:
                for check_identifier in state.spaceships_occupied_identifiers:
                    x, y, z, spaceship_name = check_identifier
                    check_coordinates = (x, y, z)
                    if current_coordinates == check_coordinates:
                        new_coordinates = UtilsActions.move_me_anywhere(check_coordinates, state, grid_size,
                                                                        not_in_direction)

                        if new_coordinates:
                            return (new_coordinates, spaceship_name)
                        break

        return None, None

    @staticmethod
    def check_within_grid_range(current_coordinates, grid_size):
        if print_all_headlines:
            print(">>> Function: check_within_grid_range")
        x, y, z = current_coordinates
        grid_legalization_part_1 = x < grid_size and y < grid_size and z < grid_size
        grid_legalization_part_2 = x >= 0 and y >= 0 and z >= 0
        return grid_legalization_part_1 and grid_legalization_part_2

    @staticmethod
    def check_empty_cell(current_coordinates, state):
        if print_all_headlines:
            print(">>> Function: check_empty_cell")
        if current_coordinates not in state.occupied_coordinates:
            return True

    @staticmethod
    def move_me_anywhere(current_coordinates, state, grid_size, not_in_direction=None, main_ship=False):
        if print_all_headlines:
            print(">>> Function: move_me_anywhere")

        movements_set = set()
        possible_directions = UtilsActions.get_possible_directions(not_in_direction)

        for dirc in possible_directions:
            new_coordinates = UtilsActions.new_coordinates_by_direction(current_coordinates, dirc)
            if UtilsActions.check_within_grid_range(new_coordinates, grid_size) and UtilsActions.check_empty_cell(
                    new_coordinates, state):
                if main_ship:
                    movements_set.add(new_coordinates)
                else:
                    return new_coordinates

        if not_in_direction:
            new_coordinates = UtilsActions.new_coordinates_by_direction(current_coordinates, not_in_direction)
            if UtilsActions.check_within_grid_range(new_coordinates, grid_size) and UtilsActions.check_empty_cell(
                    new_coordinates, state):
                if main_ship:
                    movements_set.add(new_coordinates)
                else:
                    return new_coordinates

        if main_ship:
            return movements_set
        return None

    @staticmethod
    def get_possible_directions(dirc_filter=None):
        possible_directions = ['dx', 'dy', 'dz', '-dx', '-dy', '-dz']
        if dirc_filter:
            for current_dirc in dirc_filter:
                possible_directions.remove(current_dirc)

        return possible_directions

    @staticmethod
    def new_coordinates_by_direction(current_coordinates, direction):
        if print_all_headlines:
            print(">>> Function: new_coordinates_by_direction")
        if direction == 'dx':
            return (current_coordinates[0] + 1, current_coordinates[1], current_coordinates[2])
        elif direction == '-dx':
            return (current_coordinates[0] - 1, current_coordinates[1], current_coordinates[2])
        elif direction == 'dy':
            return (current_coordinates[0], current_coordinates[1] + 1, current_coordinates[2])
        elif direction == '-dy':
            return (current_coordinates[0], current_coordinates[1] - 1, current_coordinates[2])
        elif direction == 'dz':
            return (current_coordinates[0], current_coordinates[1], current_coordinates[2] + 1)
        else:
            return (current_coordinates[0], current_coordinates[1], current_coordinates[2] - 1)

    @staticmethod
    def check_straight_line(tuple_coordinate1, tuple_coordinate2):
        if print_all_headlines:
            print(">>> Function: check_straight_line")
        dx = tuple_coordinate2[0] - tuple_coordinate1[0]
        dy = tuple_coordinate2[1] - tuple_coordinate1[1]
        dz = tuple_coordinate2[2] - tuple_coordinate1[2]

        if dx == 0 and dy == 0:
            return (dz, 'dz', 1) if dz > 0 else (-dz, '-dz', 1)

        if dx == 0 and dz == 0:
            return (dy, 'dy', 1) if dy > 0 else (-dy, '-dy', 1)

        if dy == 0 and dz == 0:
            return (dx, 'dx', 1) if dx > 0 else (-dx, '-dx', 1)

        distances_to_return = []
        directions_to_return = []
        if dx:
            if dx > 0:
                distances_to_return.append(dx)
                directions_to_return.append('dx')
            else:
                distances_to_return.append(-dx)
                directions_to_return.append('-dx')

        if dy:
            if dy > 0:
                distances_to_return.append(dy)
                directions_to_return.append('dy')
            else:
                distances_to_return.append(-dy)
                directions_to_return.append('-dy')

        if dz:
            if dz > 0:
                distances_to_return.append(dz)
                directions_to_return.append('dz')
            else:
                distances_to_return.append(-dz)
                directions_to_return.append('-dz')

        return distances_to_return, directions_to_return, 0


class MyState:
    def __init__(self):
        self.targets_hit = set()
        self.devices_status = set()
        self.occupied_coordinates = set()
        self.spaceships_occupied_identifiers = set()

    def assign_all_variables(self, targets_occupied_coordinates, spaceships_occupied_coordinates, targets_hit_set,
                             devices_status_set):
        self.occupied_coordinates = targets_occupied_coordinates
        self.spaceships_occupied_identifiers = spaceships_occupied_coordinates
        self.targets_hit = targets_hit_set
        self.devices_status = devices_status_set

    def add_target_occupied_coordinate(self, occupied_coordinate):
        self.occupied_coordinates.add(occupied_coordinate)

    def add_spaceship_occupied_coordinate(self, occupied_coordinate, occupied_identifier):
        self.occupied_coordinates.add(occupied_coordinate)
        self.spaceships_occupied_identifiers.add(occupied_identifier)

    def remove_spaceship_occupied_coordinate(self, occupied_coordinate, occupied_identifier):
        self.occupied_coordinates.remove(occupied_coordinate)
        self.spaceships_occupied_identifiers.remove(occupied_identifier)

    def add_target_hit(self, target_hit_tuple):
        self.targets_hit.add(target_hit_tuple)

    def add_device_status(self, device_status_tuple):
        self.devices_status.add(device_status_tuple)

    def remove_device_status(self, device_status_tuple):
        self.devices_status.remove(device_status_tuple)

    def __hash__(self):
        return hash((frozenset(self.occupied_coordinates), frozenset(self.spaceships_occupied_identifiers),
                     frozenset(self.targets_hit), frozenset(self.devices_status)))

    def __eq__(self, other):
        return self.occupied_coordinates == other.occupied_coordinates \
               and self.spaceships_occupied_identifiers == other.spaceships_occupied_identifiers \
               and self.targets_hit == other.targets_hit \
               and set(self.devices_status) == set(other.devices_status)


class Spaceship:
    def __init__(self, coordinates, name, devices):
        self.coordinates = coordinates
        self.name = name
        self.assigned_targets = set()

        self.devices = devices
        self.devices_onoff = {}
        self.devices_calibration = {}
        self.active_device = None

        self.initialize_devices_state()

    def initialize_devices_state(self):
        for current_device in self.devices:
            if current_device not in self.devices_onoff.keys():
                self.devices_onoff[current_device] = 0
                self.devices_calibration[current_device] = 0

    def check_ready_fire(self, device):
        if self.check_device_exists(device):
            if self.devices_onoff[device] == 1 and self.devices_calibration[device] == 1:
                return True
        return False

    def check_ready_calibrate(self, device):
        if self.check_device_exists(device):
            if self.devices_onoff[device] == 1 and self.devices_calibration[device] == 0:
                return True
        return False

    def check_ready_turnon(self, device):
        if self.check_device_exists(device):
            if self.devices_onoff[device] == 0:
                return True
        return False

    def check_device_exists(self, device):
        if device in self.devices:
            return True
        return False

    def calibrate_device(self, device):
        value_to_remove = None
        value_to_add = None
        if self.active_device:
            value_to_remove = self.get_tuple_active_device()
        # else:
        #   print("DELETE ME: CAN'T BE HERE.")
        self.devices_calibration[device] = 1
        value_to_add = self.get_tuple_active_device()
        return value_to_remove, value_to_add

    def turn_on_device(self, device):
        self.devices_onoff[device] = 1
        self.active_device = device
        return self.get_tuple_active_device()

    def turn_off_devices(self):
        value_to_return = None
        if self.active_device:
            value_to_return = self.get_tuple_active_device()
        self.i_said_turnoff()
        return value_to_return

    def i_said_turnoff(self):
        self.devices_onoff = {key: 0 for key in self.devices_onoff}
        self.devices_calibration = {key: 0 for key in self.devices_calibration}
        self.active_device = None

    def get_tuple_active_device(self):
        if self.devices_calibration[self.active_device] != 0:
            return (self.name, self.active_device, 1, 1)
        else:
            return (self.name, self.active_device, 1, 0)

    def get_spaceship_identifier(self):
        return (self.coordinates + (self.name,))


class KBManager:
    def __init__(self):
        self.space_kb = logic.PropKB()
        self.single_expressions_set = set()

    def tell_single_cell(self, current_expr, safety):
        if current_expr not in self.single_expressions_set:
            self.single_expressions_set.add(current_expr)
            if safety:
                self.tell(~current_expr)
            else:
                self.tell(current_expr)

    def tell(self, sentence):
        """Add the sentence's clauses to the KB."""
        print("Function: KB_Manager.tell >> Printing Sentence: ", sentence)
        self.space_kb.extend(logic.conjuncts(logic.to_cnf(sentence)))

    def ask_generator(self, query):
        """Yield the empty substitution {} if KB entails query; else no results."""
        if logic.tt_entails(logic.Expr('&', *self.space_kb), query):
            yield {}

    def ask_if_true(self, query):
        """Return True if the KB entails query, else return False."""
        for _ in self.ask_generator(query):
            return True
        return False

    def retract(self, sentence):
        """Remove the sentence's clauses from the KB."""
        for c in logic.conjuncts(logic.to_cnf(sentence)):
            if c in self.space_kb:
                self.space_kb.remove(c)

    def get_result(self, to_check):
        result = logic.dpll_satisfiable(
            logic.to_cnf(logic.associate('&', self.space_kb.clauses + [logic.expr(to_check)])))
        return result


class Space3DCell:
    def __init__(self, coordinates, data=0):
        self.coordinates = coordinates
        self.cell_expr = self.create_expression()
        self.cell_indication_expr = self.create_indication_expression()

        self.dead_end_dict = dict()  # [ship_name] : [destination_coordinates1, destination_coordinates2, ...]

        self.explored = False
        self.explored_by = set()

        self.has_indication = False  # Remember that if unexplored and false then it's unknown
        self.safe = 0  # 1 = Safe, -1 = Fire, 0 = Unknown

    def explored_by_ship(self, ship_name):
        if ship_name in self.explored_by:
            return True
        return False

    def create_expression(self):
        x, y, z = self.coordinates
        current_expr = "L" + str(x) + str(y) + str(z)
        return logic.expr(current_expr)

    def create_indication_expression(self):
        x, y, z = self.coordinates
        current_expr = "I" + str(x) + str(y) + str(z)
        return logic.expr(current_expr)

    def set_explored(self, spaceship_name):
        self.explored = True
        self.add_explored_by(spaceship_name)

    def add_explored_by(self, spaceship_name):
        if spaceship_name not in self.explored_by:
            self.explored_by.add(spaceship_name)

    def set_safe(self, guru):
        if not self.safe:
            guru.tell_single_cell(self.cell_expr, True)
            self.safe = 1

    def set_fire(self, guru):
        guru.tell_single_cell(self.cell_expr, False)
        self.safe = -1


class Space3DGrid:
    def __init__(self, grid_size):
        self.grid_size = grid_size
        self.grid = [[[Space3DCell((i, j, k)) for k in range(grid_size)] for j in range(grid_size)] for i in
                     range(grid_size)]

        self.active_targets = set()
        self.spaceships = []
        self.calibration_targets = []

    def check_within_grid_range(self, current_coordinates):
        x, y, z = current_coordinates
        grid_legalization_part_1 = x < self.grid_size and y < self.grid_size and z < self.grid_size
        grid_legalization_part_2 = x >= 0 and y >= 0 and z >= 0
        return grid_legalization_part_1 and grid_legalization_part_2

    def get_cell(self, coordinates):
        x, y, z = coordinates
        return self.grid[x][y][z]


class GridManager:
    def __init__(self, grid_size):
        self.grid_obj = Space3DGrid(grid_size)
        self.guru = KBManager()
        self.safe_dict = {'x': set(), 'y': set(), 'z': set()}
        self.fire_dict = {'x': set(), 'y': set(), 'z': set()}
        self.safe_but_unexplored = []

    # --------------------------------- #

    def get_closest_explore_to_cell(self, target_coordinates, ship_name=None):
        if not self.safe_but_unexplored:
            return None

        min_distance = 999
        min_index = 0
        for ind, current_coordinates in enumerate(self.safe_but_unexplored):
            if self.grid_obj.get_cell(current_coordinates).explored_by_ship(ship_name)
            dx, dy, dz = abs(target_coordinates[0] - current_coordinates[0]), abs(
                target_coordinates[1] - current_coordinates[1]), abs(target_coordinates[2] - current_coordinates[2])

            dist = (dx + dy + dz) - max(dx, dy, dz)
            if dist < min_distance:
                min_distance = dist
                min_index = ind

        if min_distance < 999:
            return self.safe_but_unexplored[min_index]
        return None

    def get_best_random_move(self, coordinates_list):
        def get_rating(current_coordinates):
            x, y, z = current_coordinates
            voting = 0

            if (y, z) in self.safe_dict['x']:
                voting += 1
            elif (y, z) in self.fire_dict['x']:
                voting -= 1

            if (x, z) in self.safe_dict['y']:
                voting += 1
            elif (x, z) in self.fire_dict['y']:
                voting -= 1

            if (x, y) in self.safe_dict['z']:
                voting += 1
            elif (x, y) in self.safe_dict['z']:
                voting -= 1

            return voting

        max_value = -999
        max_index = 0

        for current_index in range(len(coordinates_list)):
            current_coordinates = coordinates_list[current_index]
            current_vote = get_rating(current_coordinates)
            if max_value < current_vote:
                max_value = current_vote
                max_index = current_index

        return max_index

    # --------------------------------- #

    def check_add_cell_spaceship(self, cell_coordinates, ship_name):
        cell_obj = self.grid_obj.get_cell(cell_coordinates)
        if not cell_obj.explored_by_ship(ship_name):
            cell_obj.add_explored_by(ship_name)

    def get_safe_unexplored_cells_filo(self, ship_name=None):
        for current_coordinates in reversed(self.safe_but_unexplored):
            if not ship_name:
                yield self.grid_obj.get_cell(current_coordinates)
            else:
                if self.grid_obj.get_cell(current_coordinates).explored_by_ship(ship_name):
                    yield self.grid_obj.get_cell((current_coordinates))

    # --------------------------------- #

    def check_action_destination_safety(self, destination_coordinates, try_hard=False):
        current_cell = self.grid_obj.get_cell(destination_coordinates)
        if current_cell.safe == 1:
            return True
        elif current_cell.safe == -1:
            return False
        else:
            status_code = self.check_coordinates_status_local(destination_coordinates)
            if status_code == 1:
                return True
            elif status_code == -1:
                return False
            elif try_hard:
                current_result = self.guru.get_result(current_cell.cell_expr)
                if not current_result:
                    return True
                return False
            return False

    def try_extract_observation_data(self, current_cell, current_spaceship_name, observation):
        x, y, z = current_cell.coordinates
        px = (x - 1, y, z)
        nx = (x + 1, y, z)
        py = (x, y - 1, z)
        ny = (x, y + 1, z)
        pz = (x, y, z - 1)
        nz = (x, y, z + 1)

        legal_cells = 0
        safe_cells = []
        unknown_cells = []
        fire_cells = []

        # Previous X
        current_cell = px
        if self.grid_obj.check_within_grid_range(current_cell):
            legal_cells += 1
            current_cell = self.grid_obj.get_cell(current_cell)
            if current_cell.safe == 1:
                safe_cells.append(current_cell)
            elif current_cell.safe == -1:
                fire_cells.append(current_cell)
            else:
                status = self.check_coordinates_status_local(px)
                if status == 1:
                    current_cell.set_safe(self.guru)
                    safe_cells.append(current_cell)
                elif status == -1:
                    current_cell.set_fire(self.guru)
                    fire_cells.append(current_cell)
                else:
                    unknown_cells.append(current_cell)

        # Next X
        current_cell = nx
        if self.grid_obj.check_within_grid_range(current_cell):
            legal_cells += 1
            current_cell = self.grid_obj.get_cell(current_cell)
            if current_cell.safe == 1:
                safe_cells.append(current_cell)
            elif current_cell.safe == -1:
                fire_cells.append(current_cell)
            else:
                status = self.check_coordinates_status_local(nx)
                if status == 1:
                    current_cell.set_safe(self.guru)
                    safe_cells.append(current_cell)
                elif status == -1:
                    current_cell.set_fire(self.guru)
                    fire_cells.append(current_cell)
                else:
                    unknown_cells.append(current_cell)

        # Previous Y
        current_cell = py
        if self.grid_obj.check_within_grid_range(current_cell):
            legal_cells += 1
            current_cell = self.grid_obj.get_cell(current_cell)
            if current_cell.safe == 1:
                safe_cells.append(current_cell)
            elif current_cell.safe == -1:
                fire_cells.append(current_cell)
            else:
                status = self.check_coordinates_status_local(py)
                if status == 1:
                    current_cell.set_safe(self.guru)
                    safe_cells.append(current_cell)
                elif status == -1:
                    current_cell.set_fire(self.guru)
                    fire_cells.append(current_cell)
                else:
                    unknown_cells.append(current_cell)

        # Next Y
        current_cell = ny
        if self.grid_obj.check_within_grid_range(current_cell):
            legal_cells += 1
            current_cell = self.grid_obj.get_cell(current_cell)
            if current_cell.safe == 1:
                safe_cells.append(current_cell)
            elif current_cell.safe == -1:
                fire_cells.append(current_cell)
            else:
                status = self.check_coordinates_status_local(ny)
                if status == 1:
                    current_cell.set_safe(self.guru)
                    safe_cells.append(current_cell)
                elif status == -1:
                    current_cell.set_fire(self.guru)
                    fire_cells.append(current_cell)
                else:
                    unknown_cells.append(current_cell)

        # Previous Z
        current_cell = pz
        if self.grid_obj.check_within_grid_range(current_cell):
            legal_cells += 1
            current_cell = self.grid_obj.get_cell(current_cell)
            if current_cell.safe == 1:
                safe_cells.append(current_cell)
            elif current_cell.safe == -1:
                fire_cells.append(current_cell)
            else:
                status = self.check_coordinates_status_local(pz)
                if status == 1:
                    current_cell.set_safe(self.guru)
                    safe_cells.append(current_cell)
                elif status == -1:
                    current_cell.set_fire(self.guru)
                    fire_cells.append(current_cell)
                else:
                    unknown_cells.append(current_cell)

        # Next Z
        current_cell = nz
        if self.grid_obj.check_within_grid_range(current_cell):
            legal_cells += 1
            current_cell = self.grid_obj.get_cell(current_cell)
            if current_cell.safe == 1:
                safe_cells.append(current_cell)
            elif current_cell.safe == -1:
                fire_cells.append(current_cell)
            else:
                status = self.check_coordinates_status_local(nz)
                if status == 1:
                    current_cell.set_safe(self.guru)
                    safe_cells.append(current_cell)
                elif status == -1:
                    current_cell.set_fire(self.guru)
                    fire_cells.append(current_cell)
                else:
                    unknown_cells.append(current_cell)

        count_safe = len(safe_cells)
        count_fire = len(fire_cells)
        count_unkw = len(unknown_cells)

        if count_fire + count_safe != legal_cells:
            if count_fire == observation:
                for current_cell in unknown_cells:
                    self.add_safe_coordinates_data(current_cell, current_spaceship_name)

            elif observation - count_fire == count_unkw:
                for current_cell in unknown_cells:
                    self.add_fire_coordinates_data(current_cell)

            '''
            else:
                for current_cell in unknown_cells:
                    if self.check_coordinates_safety_kb(current_cell):
                        current_cell.set_safe(self.guru)
            '''

        self.make_neighbors_then_tell_sentence(current_cell)

    # --------------------------------- #

    def check_coordinates_status_local(self, coordinates):
        x, y, z = coordinates
        if (y, z) in self.safe_dict['x'] and (x, z) in self.safe_dict['y'] and (x, y) in self.safe_dict['z']:
            return 1
        if (y, z) in self.fire_dict['x'] and (x, z) in self.fire_dict['y'] and (x, y) in self.fire_dict['z']:
            return -1
        return 0

    def check_coordinates_safety_kb(self, current_cell):
        current_cell_expr = current_cell.cell_expr
        current_result = self.guru.get_result(current_cell_expr)
        if not current_result:
            return True
        return False

    # --------------------------------- #

    def add_explored_coordinates_data(self, coordinates, current_spaceship_name, observation):
        current_cell = self.grid_obj.get_cell(coordinates)
        current_cell.set_explored(current_spaceship_name)
        if coordinates in self.safe_but_unexplored:
            self.safe_but_unexplored.remove(coordinates)

        self.add_safe_coordinates_data(current_cell, current_spaceship_name)
        if observation == 0:
            self.add_zero_observation_coordinates_data(current_cell, current_spaceship_name)
        elif observation == -1:
            self.add_fire_coordinates_data(current_cell)
        else:
            current_cell.has_indication = True
            self.try_extract_observation_data(current_cell, current_spaceship_name, observation)

    def add_fire_coordinates_data(self, current_cell):
        x, y, z = current_cell.coordinates
        current_cell.set_fire(self.guru)

        if (y, z) not in self.fire_dict['x']:
            self.add_fire_x((y, z))
        if (x, z) not in self.fire_dict['y']:
            self.add_fire_y((x, z))
        if (x, y) not in self.fire_dict['z']:
            self.add_fire_z((x, y))

        self.make_neighbors_then_tell_sentence(current_cell)

    # --------------------------------- #

    def make_neighbors_then_tell_sentence(self, current_cell):
        x, y, z = current_cell.coordinates

        px = None
        nx = None
        py = None
        ny = None
        pz = None
        nz = None

        if self.grid_obj.check_within_grid_range((x - 1, y, z)):
            px = self.grid_obj.get_cell((x - 1, y, z))

        if self.grid_obj.check_within_grid_range((x + 1, y, z)):
            nx = self.grid_obj.get_cell((x + 1, y, z))

        if self.grid_obj.check_within_grid_range((x, y - 1, z)):
            py = self.grid_obj.get_cell((x, y - 1, z))

        if self.grid_obj.check_within_grid_range((x, y + 1, z)):
            ny = self.grid_obj.get_cell((x, y + 1, z))

        if self.grid_obj.check_within_grid_range((x, y, z - 1)):
            pz = self.grid_obj.get_cell((x, y, z - 1))

        if self.grid_obj.check_within_grid_range((x, y, z + 1)):
            nz = self.grid_obj.get_cell((x, y, z + 1))

        self.make_and_tell_sentence(current_cell, px, nx, py, ny, pz, nz)

    def make_and_tell_sentence(self, current_cell, *rest):
        first_add = True

        sentence = current_cell.cell_indication_expr
        sentence = sentence + " | '<=>' | (("
        for current_cell in rest:
            if current_cell:
                if first_add:
                    first_add = False
                    sentence = sentence + current_cell.cell_expr
                else:
                    sentence = sentence + " | "
                    sentence = sentence + current_cell.cell_expr

        sentence = sentence + "))"
        self.guru.tell(sentence)

    # --------------------------------- #

    def add_zero_observation_coordinates_data(self, current_cell, current_spaceship_name):
        x, y, z = current_cell.coordinates

        px = self.add_safe_coordinate_data_wvalidation((x - 1, y, z), current_spaceship_name)
        nx = self.add_safe_coordinate_data_wvalidation((x + 1, y, z), current_spaceship_name)
        py = self.add_safe_coordinate_data_wvalidation((x, y - 1, z), current_spaceship_name)
        ny = self.add_safe_coordinate_data_wvalidation((x, y + 1, z), current_spaceship_name)
        pz = self.add_safe_coordinate_data_wvalidation((x, y, z - 1), current_spaceship_name)
        nz = self.add_safe_coordinate_data_wvalidation((x, y, z + 1), current_spaceship_name)

        self.make_and_tell_sentence(current_cell, px, nx, py, ny, pz, nz)

    def add_safe_coordinate_data_wvalidation(self, coordinates, current_spaceship_name):
        if self.grid_obj.check_within_grid_range(coordinates):
            current_cell = self.grid_obj.get_cell(coordinates)
            self.add_safe_coordinates_data(current_cell, current_spaceship_name)
            return current_cell
        return None

    def add_safe_coordinates_data(self, current_cell, current_spaceship_name):
        current_cell.set_safe(self.guru)
        coordinates = current_cell.coordinates
        x, y, z = coordinates

        if not current_cell.explored:
            current_cell.add_explored_by(current_spaceship_name)
            if coordinates not in self.safe_but_unexplored:
                self.safe_but_unexplored.append(coordinates)

        if (y, z) not in self.safe_dict['x']:
            self.add_safe_x((y, z))
        if (x, z) not in self.safe_dict['y']:
            self.add_safe_y((x, z))
        if (x, y) not in self.safe_dict['z']:
            self.add_safe_z((x, y))

    # --------------------------------- #

    def add_safe_x(self, y_z):
        self.safe_dict['x'].add(y_z)

    def add_safe_y(self, x_z):
        self.safe_dict['y'].add(x_z)

    def add_safe_z(self, x_y):
        self.safe_dict['z'].add(x_y)

    # --------------------------------- #

    def add_fire_x(self, y_z):
        self.fire_dict['x'].add(y_z)

    def add_fire_y(self, x_z):
        self.fire_dict['y'].add(x_z)

    def add_fire_z(self, x_y):
        self.fire_dict['z'].add(x_y)


class Overview:
    def __init__(self, grid_size):
        self.grid_size = grid_size
        self.state = MyState()
        self.devices = None
        self.spaceships = {}  # [spaceship_name] : spaceship_object
        self.targets_dict = {}  # [target_coordinate] : target_devices
        self.calibration_targets_dict = {}  # [device_name] : target_coordinates
        self.total_number_of_hits = 0
        self.total_number_of_hits_per_device = dict()

        self.calib_priority_manager = CalibPriorityManager(self)
        self.target_priority_manager = TargetPriorityManager(self)

        self.dictionary_device_spaceships_priorities = dict()  # Calib
        self.dictionary_device_targets_priorities = dict()  # Use
        self.online_device_id = 0
        self.is_turned_on = 0
        self.is_calibrated = 0
        self.calibration_current_estimate_index = 0
        self.use_device_current_estimate_index = 0
        self.undo_actions_dict = dict()  # [ship_name] : undo_action

        self.exploration_mode = 0
        self.exploration_plan = None  # Will be a dict [ship_name] : action moves
        self.grid_manager_first_introduction = True

    def set_spaceship_cells(self, ship_names, ship_initial_coordinates, ship_devices):
        for current_spaceship_name in ship_names:
            current_spaceship_coordinates = ship_initial_coordinates[current_spaceship_name]
            current_spaceship_devices = ship_devices[current_spaceship_name]
            created_ship = Spaceship(current_spaceship_coordinates, current_spaceship_name, current_spaceship_devices)
            self.spaceships[current_spaceship_name] = created_ship
            self.state.add_spaceship_occupied_coordinate(current_spaceship_coordinates,
                                                         created_ship.get_spaceship_identifier())

    def set_targets_cells(self, dict_coordinate_devices):
        self.targets_dict = dict_coordinate_devices
        [self.state.add_target_occupied_coordinate(current_coordinates) for current_coordinates in
         dict_coordinate_devices]
        self.total_number_of_hits = sum(len(tuple_of_devices) for tuple_of_devices in dict_coordinate_devices.values())

        for current_device in self.devices:
            count_instances = 0
            for current_target_devices in self.targets_dict.values():
                if current_device in current_target_devices:
                    count_instances += 1
            self.total_number_of_hits_per_device[current_device] = count_instances

    def set_calibration_targets_cells(self, dict_devices_coordinates):
        self.calibration_targets_dict = dict_devices_coordinates
        [self.state.add_target_occupied_coordinate(dict_devices_coordinates[current_device]) for current_device in
         dict_devices_coordinates]

    def set_devices(self, devices_tuple):
        self.devices = devices_tuple

    def goal_test(self):
        if len(self.state.targets_hit) < self.total_number_of_hits:
            return False
        return True

    def update_current_observation(self, grid_manager, observation, current_spaceship_name):
        if self.grid_manager_first_introduction:
            self.grid_manager_first_introduction = False
            for current_spaceship in self.spaceships:
                current_spaceship_coordinates = self.spaceships[current_spaceship].coordinates
                if current_spaceship not in observation:
                    grid_manager.add_explored_coordinates_data(current_spaceship_coordinates, current_spaceship_name, 0)
                else:
                    grid_manager.add_explored_coordinates_data(current_spaceship_coordinates, current_spaceship_name,
                                                               observation[current_spaceship_name])
        else:
            current_spaceship_coordinates = self.spaceships[current_spaceship_name].coordinates
            if current_spaceship_name not in observation:
                grid_manager.add_explored_coordinates_data(current_spaceship_coordinates, current_spaceship_name, 0)
            else:
                grid_manager.add_explored_coordinates_data(current_spaceship_coordinates, current_spaceship_name,
                                                           observation[current_spaceship_name])

    def get_possible_actions(self, grid_manager, observation):
        if print_all_headlines or print_main_headlines:
            print(">>> Function: get_possible_actions")

        if self.exploration_plan:
            for current_ship in self.exploration_plan:
                current_move_action = self.exploration_plan[current_ship][-1]
                del self.exploration_plan[current_ship][-1]
                return current_move_action

        current_device = self.devices[self.online_device_id]
        current_device_estimate = self.dictionary_device_spaceships_priorities[current_device][
            self.calibration_current_estimate_index]
        current_estimate_spaceship = current_device_estimate[0]
        current_estimate_spaceship_name = current_estimate_spaceship.name

        self.update_current_observation(grid_manager, observation, current_estimate_spaceship_name)

        if not self.is_calibrated:
            all_possible_actions = self.calib_priority_manager.get_calibration_actions()
            for current_possible_action in all_possible_actions:
                if current_possible_action[0] == 'move':
                    if grid_manager.check_action_destination_safety(current_possible_action[3], True):
                        return current_possible_action
                else:
                    return current_possible_action

            current_device_calibration_coordinate = self.calibration_targets_dict[current_device]
            cell_to_explore = grid_manager.get_closest_explore_to_cell(current_device_calibration_coordinate)
            if cell_to_explore:
                p = SmallProblemManager()

            # Go on exploration while adding current priority which is defined by ship -> target coordinates to
            # uncertain priorities set. After exploration done, check all uncertain priorities if changed.
            # If yes go by one of them, else explore some more

        else:
            return self.target_priority_manager.get_target_actions()

    def check_active_devices(self):
        if print_all_headlines:
            print(">>> Function: check_active_devices")

        current_device = self.devices[self.online_device_id]
        if current_device not in self.dictionary_device_spaceships_priorities:  # Only gets here on first time entrance
            self.calib_priority_manager.priority_calib_main()

        if not self.dictionary_device_spaceships_priorities[current_device]:
            if self.total_number_of_hits_per_device[current_device] == 0:
                self.calib_priority_manager.priority_calib_main()

    def update_action(self, action):
        if print_all_headlines or print_main_headlines:
            print("\n>>> Function: update_action")

        UtilsUpdate.distribute_packet(action, self.spaceships, self.targets_dict, self.state)
        if action[0] == 'move':
            if not self.exploration_mode:
                if self.is_calibrated:
                    self.target_priority_manager.priority_target_update()
                else:
                    self.calib_priority_manager.priority_calib_update()

        elif action[0] == 'turn_on':
            self.is_turned_on = 1
        elif action[0] == 'calibrate':
            self.is_calibrated = 1
            self.target_priority_manager.priority_target_main()
        elif action[0] == 'use':
            action_device = action[2]
            self.total_number_of_hits_per_device[action_device] -= 1

            if self.total_number_of_hits_per_device[action_device] == 0:
                self.dictionary_device_spaceships_priorities[action_device] = None
                self.dictionary_device_targets_priorities[action_device] = None
            else:
                self.target_priority_manager.priority_target_main()

        self.check_active_devices()

    def __hash__(self):
        return hash((self.state))

    def __eq__(self, other):
        is_equal = self.state == other.state
        return is_equal

    def __lt__(self, node):
        return self.heuristic_value < node.heuristic_value


class SpaceshipController:
    "This class is a controller for a spaceship problem."

    def __init__(self, problem, num_of_transmitters):
        self.state = self.unpack_problem(problem)
        self.state.set_number_of_transmitters(num_of_transmitters)
        self.grid_manager = None
        self.first_observation_initialization = True
        search.Problem.__init__(self, initial=self.state)

    def unpack_problem(self, initial):
        grid_size = initial[0]  # Integer
        self.grid_manager = GridManager(grid_size)

        spaceships_names = initial[1]  # Tuple of Strings
        devices = initial[2]  # Tuple of Strings
        ships_devices = initial[3]  # Dictionary of Tuples
        calibration_targets = initial[4]  # Dictionary of Tuples
        targets = initial[5]  # Dictionary of Tuples
        initial_positions = initial[6]  # Dictionary of Tuples

        state = Overview(grid_size)
        state.set_spaceship_cells(spaceships_names, initial_positions, ships_devices)
        state.set_calibration_targets_cells(calibration_targets)
        state.set_devices(devices)
        state.set_targets_cells(targets)
        state.calculate_heuristic_value()
        state.check_active_devices()

        return state

    def get_next_action(self, observation):
        # ship observation -1 means ship was destroyed
        # ship observation other than -1 (it will be int>0) means number of lasers detected around ship
        print(observation)
        all_possible_actions = self.state.get_possible_actions(self.grid_manager, observation)
        for current_possible_action in all_possible_actions:
            yield current_possible_action

    def result(self, action):
        self.state.update_action(action)

    def goal_test(self, state):
        return state.goal_test()

    def h(self, node):
        return node.state.calculate_heuristic_value()

# TODO : COMPLETE BY STUDENTS
# get observation for the current state and return next action to apply (and None if no action is applicable)
