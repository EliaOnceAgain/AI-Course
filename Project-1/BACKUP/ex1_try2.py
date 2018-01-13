import search
import random
import math


ids = ["204657977"]

class UtilsActions():
    @staticmethod
    def get_possible_movements(current_spaceship, occupied_coordinates, grid_size):
        '''
        A function to check a spaceship's possible moves
        :param current_spaceship: Spaceship object to check it's possible moves
        :param occupied_coordinates:  set of occupied coordinates to limit the spaceship's possible moves
        :param grid_size:  size of the space grid to limit the spaceship's possible moves
        :return:
            A Set of possible moves
        '''
        current_coordinates = current_spaceship.coordinates
        current_name = current_spaceship.name
        possible_movements_set = set()

        if current_coordinates[0] < grid_size - 1:
            new_coordinates = (current_coordinates[0] + 1, current_coordinates[1], current_coordinates[2])
            if new_coordinates not in occupied_coordinates:
                possible_movements_set.add(("move", current_name, current_coordinates, new_coordinates))

        if current_coordinates[1] < grid_size - 1:
            new_coordinates = (current_coordinates[0], current_coordinates[1] + 1, current_coordinates[2])
            if new_coordinates not in occupied_coordinates:
                possible_movements_set.add(("move", current_name, current_coordinates, new_coordinates))

        if current_coordinates[2] < grid_size - 1:
            new_coordinates = (current_coordinates[0], current_coordinates[1], current_coordinates[2] + 1)
            if new_coordinates not in occupied_coordinates:
                possible_movements_set.add(("move", current_name, current_coordinates, new_coordinates))

        if current_coordinates[0] > 0:
            new_coordinates = (current_coordinates[0] - 1, current_coordinates[1], current_coordinates[2])
            if new_coordinates not in occupied_coordinates:
                possible_movements_set.add(("move", current_name, current_coordinates, new_coordinates))

        if current_coordinates[1] > 0:
            new_coordinates = (current_coordinates[0], current_coordinates[1] - 1, current_coordinates[2])
            if new_coordinates not in occupied_coordinates:
                possible_movements_set.add(("move", current_name, current_coordinates, new_coordinates))

        if current_coordinates[2] > 0:
            new_coordinates = (current_coordinates[0], current_coordinates[1], current_coordinates[2] - 1)
            if new_coordinates not in occupied_coordinates:
                possible_movements_set.add(("move", current_name, current_coordinates, new_coordinates))

        return possible_movements_set

    @staticmethod
    def get_possible_targets(current_spaceship, targets_dict, occupied_coordinates):
        current_coordinates = current_spaceship.coordinates
        current_name = current_spaceship.name
        possible_targets_set = set()
        for current_target in targets_dict:
            if UtilsActions.check_straight_line(current_coordinates, current_target):
                for current_target_device in targets_dict[current_target]:
                    if current_spaceship.check_ready_fire(current_target_device):
                        possible_targets_set.add(("use", current_name, current_target_device, current_target))
                        break

    @staticmethod
    def check_straight_line(tuple_coordinate1, tuple_coordinate2):
        dx = tuple_coordinate2[0] - tuple_coordinate1[0]
        dy = tuple_coordinate2[1] - tuple_coordinate1[1]
        dz = tuple_coordinate2[2] - tuple_coordinate1[2]
        if (dx == 0 and dy == 0) or (dx == 0 and dz == 0) or (dy == 0 and dz == 0):
            return True
        return False

    @staticmethod
    def check_possible_calibrations(current_spaceship, calibration_targets_dict, occupied_coodinates):


class Overview():
    def __init__(self, grid_size):
        self.grid_size = grid_size

        self.occupied_coordinates = set()

        self.spaceships = [] # Contains Spaceship objects

        self.targets_dict = None

        self.calibration_targets_dict = None

    def get_possible_movements(self, coordinates, grid_size):
        possible_movements_set = set()
        for current_spaceship in self.spaceships:
            possible_movements_set.update(
                UtilsActions.get_possible_movements(current_spaceship, self.occupied_coordinates,
                                                    self.grid_size))

    def get_possible_devices_options(self):
        possible_targets_set = set()
        for current_spaceship in self.spaceships:
            pass


    def add_occupied(self, coordinates):
        self.occupied_coordinates.add(coordinates)

    def goal_test(self):
        if self.targets_dict:
            return False
        return True

    def get_current_state(self):
        return self.occupied_coordinates

    def set_calibration_targets_cells(self, dict_devices_coordinates):
        self.calibration_targets_dict = dict_devices_coordinates

        # Add Targets coordinates to Occupied Coordinates Attribute 'self.occupied_coordinates'
        [self.add_occupied(dict_devices_coordinates[current_device]) for current_device in
         dict_devices_coordinates.keys()]

    def set_targets_cells(self, dict_coordinate_devices):
        self.targets_dict = dict_coordinate_devices

        # Add Targets coordinates to Occupied Coordinates Attribute 'self.occupied_coordinates'
        [self.add_occupied(current_coordinates) for current_coordinates in
        dict_coordinate_devices.keys()]

    def set_spaceship_cells(self, ship_names, ship_initial_coordinates, ship_devices):
        def map_spaceships(ship_coordinates, ship_name, ship_devices):
            created_ship = Spaceship(ship_coordinates, ship_name, ship_devices)
            self.add_occupied(created_ship.coordinates)
            return created_ship

        # Add Spaceships coordinates to Occupied Coordinates Attribute 'self.occupied_coordinates'
        # and save Spaceship Object
        self.spaceships = [
            map_spaceships(ship_initial_coordinates[current_name], current_name, ship_devices[current_name]) for
            current_name in ship_names]

    # def direction_calculation(self, spaceship_object, target_object):


    # def find_directions_to_targets(self):
    #     for current_spaceship in self.spaceships:
    #         for target_coordinates, target_devices in self.targets_dict.items():
    #             common_devices = set(current_spaceship.devices)&set(target_devices)
    #             if common_devices:


class Spaceship():
    def __init__(self, coordinates, name, devices):
        self.coordinates = coordinates
        self.name = name
        self.devices = devices
        self.devices_onoff = {}
        self.devices_calibration = {}

    def initialize_devices_state(self):
        for current_device in self.devices:
            if current_device not in self.devices_onoff.keys():
                self.devices_onoff[current_device] = "0"
                self.devices_calibration[current_device] = "0"

    def check_ready_fire(self, device):
        if self.devices_onoff[device] == 1 and self.devices_calibration[device] == 1:
            return True
        return False



class SpaceshipProblem(search.Problem):
    """This class implements a spaceship problem"""
    def __init__(self, initial):
        """Don't forget to set the goal or implement the goal test
        You should change the initial to your own representation"""
        self.initialize = None
        self.unpack_problem(initial)
        search.Problem.__init__(self, initial = self.initialize)

    def unpack_problem(self, initial):
        grid_size = initial[0] # Integer
        spaceships_names = initial[1] # Tuple of Strings
        devices = initial[2] # Tuple of Strings
        ships_devices = initial[3] # Dictionary of Tuples
        calibration_targets = initial[4] # Dictionary of Tuples
        targets = initial[5] # Dictionary of Tuples
        initial_positions = initial[6] # Dictionary of Tuples

        self.initialize = Overview(grid_size)
        self.initialize.set_spaceship_cells(spaceships_names, initial_positions, ships_devices)
        self.initialize.set_calibration_targets_cells(calibration_targets)
        self.initialize.set_targets_cells(targets)

    def actions(self, state):
        """Return the actions that can be executed in the given
        state. The result would typically be a tuple, but if there are
        many actions, consider yielding them one at a time in an
        iterator, rather than building them all at once."""

        # Movements to all 6 sides
        # If target in sight and device is turned on and calibrated then shoot
        # if calibration target on sight and device turned off then turn on
        # if calibration target on sight and device turned on then calibrate




    def result(self, state, action):
        """Return the state that results from executing the given
        action in the given state. The action must be one of
        self.actions(state)."""

    def goal_test(self, state):
        """ Given a state, checks if this is the goal state, compares to the created goal state"""
        return state.goal_test()

    def h(self, node):
        """ This is the heuristic. It gets a node (not a state,
        state can be accessed via node.state)
        and returns a goal distance estimate"""

    """Feel free to add your own functions"""

def create_spaceship_problem(problem, goal):
 
    return SpaceshipProblem(problem)

