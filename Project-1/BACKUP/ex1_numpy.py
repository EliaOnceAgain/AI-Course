import search
import random
import math
import numpy as np

ids = ["204657977"]


class Space3DCell():
    def __init__(self, coordinates, data=0):
        self.coordinates = coordinates
        self.data = data

    def set_data(self, data):
        if self.data == 0:
            self.data = data
        else:
            print("TO-DELETE: CELL IS NOT EMPTY.")

    def check_empty(self):
        if self.data:
            return True
        return False

    def empty_cell(self):
        self.data = 0

    def __eq__(self, other_3dcell):
        if other_3dcell is None:
            return False
        return self.data == other_3dcell.data


class Space3DGrid():
    def __init__(self, grid_size):
        self.grid_size = grid_size
        self.space_cube_3d = np.array([[[Space3DCell((i, j, k)) for k in range(grid_size)] for j in range(grid_size)] for i in
                              range(grid_size)])
        self.initialize_const_values()

        self.active_targets = set()
        self.spaceships = []
        self.calibration_targets = []

    def initialize_const_values(self):
        self.target_value = 1
        self.calib_value = 2
        self.ship_value = 3

    def get_cell(self, coordinates):
        x, y, z = coordinates
        return self.space_cube_3d[x][y][z]

    def get_grid_as_tuple(self):
        return tuple(self.space_cube_3d)

    def set_target_cell(self, coordinates):
        if coordinates not in self.active_targets:
            x, y, z = coordinates
            self.space_cube_3d[x][y][z].set_data(self.target_value)
            self.active_targets.add(coordinates)
        else:
            print("TO-DELETE: TARGET COORDINATES ALREADY EXISTS.")

    def set_calibration_cells(self, calibration_targets):
        self.calibration_targets = map(lambda current_target: Target())

    def set_calibration_cell(self, coordinates):
        x, y, z = coordinates
        self.space_cube_3d[x][y][z].set_data(self.calib_value)

    def set_spaceship_cells(self, ship_names, ship_initial_coordinates, ship_devices):
        self.spaceships = map(lambda current_name: Spaceship(ship_initial_coordinates[current_name], current_name,
                                                             ship_devices[current_name]), ship_names)

    def set_spaceship_cell(self, coordinates):
        x, y, z = coordinates
        self.space_cube_3d[x][y][z].set_data(self.ship_value)


class SpaceObject():
    def __init__(self, coordinates):
        '''
        :param coordinates: Tuple of target coordinates
        '''
        self.coordinates = coordinates


class Target(SpaceObject):
    def __init__(self, coordinates, weapons_types, is_calibration):
        '''
        :param coordinates: Tuple of target coordinates
        :param weapons_types:  Tuple of weapons types that could score the target
        '''
        SpaceObject.__init__(self, coordinates)
        self.active_devices = weapons_types
        self.is_calibration = is_calibration
        self.is_used = False


class Spaceship(SpaceObject):
    def __init__(self, coordinates, name, available_weapons):
        SpaceObject.__init__(self, coordinates)
        self.spaceship_name = name
        self.weapons = available_weapons
        self.initialize_spaceship_cell()

    def initialize_spaceship_cell(self):
        Space3DGrid.set_spaceship_cell(self.coordinates)


class SpaceshipProblem(search.Problem):
    """This class implements a spaceship problem"""

    def __init__(self, initial):
        """Don't forget to set the goal or implement the goal test
        You should change the initial to your own representation"""
        self.set_up_workspace(initial)
        search.Problem.__init__(self, initial)

    def initialize(self):
        return self.state

    def set_up_workspace(self):
        self.unpack_problem()
        self.create_model()

    def unpack_problem(self):
        self.grid_size = self.initial[0]  # Integer
        self.spaceships_names = self.initial[1]  # Tuple of Strings
        self.devices = self.initial[2]  # Tuple of Strings
        self.ships_devices = self.initial[3]  # Dictionary of Tuples
        self.calibration_targets = self.initial[4]  # Dictionary of Tuples
        self.targets = self.initial[5]  # Dictionary of Tuples
        self.initial_positions = self.initial[6]  # Dictionary of Tuples

    def create_model(self):
        self.space_grid = Space3DGrid(self.grid_size)
        self.space_grid.set_spaceship_cells(self.spaceships_names, self.initial_positions, self.ships_devices)
        self.space_grid.set_calibration_cell()

    def actions(self, state):
        """Return the actions that can be executed in the given
        state. The result would typically be a tuple, but if there are
        many actions, consider yielding them one at a time in an
        iterator, rather than building them all at once."""

    def result(self, state, action):
        """Return the state that results from executing the given
        action in the given state. The action must be one of
        self.actions(state)."""

    def goal_test(self, state):
        """ Given a state, checks if this is the goal state, compares to the created goal state"""

    def h(self, node):
        """ This is the heuristic. It gets a node (not a state,
        state can be accessed via node.state)
        and returns a goal distance estimate"""

    """Feel free to add your own functions"""

    def check_available_movements(self):
        pass


def create_spaceship_problem(problem, goal):
    return SpaceshipProblem(problem)

