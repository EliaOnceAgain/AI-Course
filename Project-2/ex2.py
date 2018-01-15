__author__ = 'sarah'

# make sure to change these to the student id's
ids = ["204657977"]

import logic
import numpy
import search
import copy
import itertools

import ex1forex2


class KB_Manager():
    def __init__(self):
        self.space_kb = logic.PropKB()

    def tell(self, sentence):
        """Add the sentence's clauses to the KB."""
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


class Space3DCell():
    def __init__(self, coordinates, data=0):
        self.coordinates = coordinates
        self.data = data
        self.suspect = False
        self.traveled = False

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
        self.grid = [[[Space3DCell((i, j, k)) for k in range(grid_size)] for j in range(grid_size)] for i in
                     range(grid_size)]
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


class GridManager:
    # Keeps track of laser lines.
    # If tile (1,2,3) is safe, it means that no lasers at whole lines x=1, y=2, z=3
    def __init__(self, grid_size):
        self.grid_obj = Space3DGrid(grid_size)
        self.safe_dict = {'x': set(), 'y': set(), 'z': set()}
        self.fire_dict = {'x': set(), 'y': set(), 'z': set()}

    def add_zero_observation_coordinate_data(self, coordinates):
        self.add_coordinate_data(True, coordinates)
        x, y, z = coordinates

        px = x - 1
        nx = x + 1
        if px not in self.safe_dict['x']:
            self.add_safe_x(px)
        if nx not in self.safe_dict['x']:
            self.add_safe_x(nx)

        py = y - 1
        ny = y + 1
        if py not in self.safe_dict['y']:
            self.add_safe_y(py)
        if ny not in self.safe_dict['y']:
            self.add_safe_y(ny)

        pz = z - 1
        nz = z + 1
        if pz not in self.safe_dict['z']:
            self.add_safe_z(pz)
        if nz not in self.safe_dict['z']:
            self.add_safe_z(nz)

    def add_coordinate_data(self, status, coordinates):
        x, y, z = coordinates
        if status:
            if x not in self.safe_dict['x']:
                self.add_safe_x(x)
            if y not in self.safe_dict['y']:
                self.add_safe_y(y)
            if z not in self.safe_dict['z']:
                self.add_safe_z(z)
        else:
            if x not in self.fire_dict['x']:
                self.add_fire_x(x)
            if y not in self.fire_dict['y']:
                self.add_fire_y(y)
            if z not in self.fire_dict['z']:
                self.add_fire_z(z)

    # --------------------------------- #

    def add_safe_x(self, x_value):
        self.safe_dict['x'].add(x_value)

    def add_safe_y(self, y_value):
        self.safe_dict['y'].add(y_value)

    def add_safe_z(self, z_value):
        self.safe_dict['z'].add(z_value)

    # --------------------------------- #

    def add_fire_x(self, x_value):
        self.fire_dict['x'].add(x_value)

    def add_fire_y(self, y_value):
        self.fire_dict['y'].add(y_value)

    def add_fire_z(self, z_value):
        self.fire_dict['z'].add(z_value)


class SpaceshipController:
    "This class is a controller for a spaceship problem."

    def __init__(self, problem, num_of_transmitters):
        self.state = self.unpack_problem(problem)
        self.state.set_number_of_transmitters(num_of_transmitters)
        self.my_grid = None
        search.Problem.__init__(self, initial=self.state)

    def unpack_problem(self, initial):
        grid_size = initial[0]  # Integer
        self.my_grid = GridManager(grid_size)

        spaceships_names = initial[1]  # Tuple of Strings
        devices = initial[2]  # Tuple of Strings
        ships_devices = initial[3]  # Dictionary of Tuples
        calibration_targets = initial[4]  # Dictionary of Tuples
        targets = initial[5]  # Dictionary of Tuples
        initial_positions = initial[6]  # Dictionary of Tuples

        state = ex1forex2.Overview(grid_size)
        state.set_spaceship_cells(spaceships_names, initial_positions, ships_devices)
        state.set_calibration_targets_cells(calibration_targets)
        state.set_devices(devices)
        state.set_targets_cells(targets)
        state.calculate_heuristic_value()
        state.check_active_devices()

        return state

    def get_next_action(self, observation, my_parameter=None):
        # ship observation -1 means ship was destroyed
        # ship observation other than -1 (it will be int>0) means number of lasers detected around ship
        print(observation)
        all_possible_actions = self.state.get_possible_actions()
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
