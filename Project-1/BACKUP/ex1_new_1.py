import search
import random
import math
from copy import deepcopy


ids = ["204657977"]

class State():
    def __init__(self):
        self.occupied_coordinates = set()
        self.targets_hit = set()
        self.devices_status = set()

    def assign_all_variables(self, occupied_coordinates_set, targets_hit_set, devices_status_set):
        self.occupied_coordinates = occupied_coordinates_set
        self.targets_hit = targets_hit_set
        self.devices_status = devices_status_set

    def assign_occupied_coordinates(self, occupied_coordinates_set):
        self.occupied_coordinates = occupied_coordinates_set

    def assign_targets_hit(self, targets_hit_set):
        self.targets_hit = targets_hit_set

    def assign_devices_status(self, devices_status_set):
        self.devices_status = devices_status_set

    def add_occupied_coordinate(self, occupied_coordinate_tuple):
        self.occupied_coordinates.add(occupied_coordinate_tuple)

    def remove_occupied_coordinate(self, occupied_coordinate_tuple):
        self.occupied_coordinates.remove(occupied_coordinate_tuple)

    def add_target_hit(self, target_hit_tuple):
        self.targets_hit.add(target_hit_tuple)

    def add_device_status(self, device_status_tuple):
        self.devices_status.add(device_status_tuple)

    def remove_device_status(self, device_status_tuple):
        self.devices_status.remove(device_status_tuple)

    def __hash__(self):
        return hash((frozenset(self.occupied_coordinates), frozenset(self.targets_hit), frozenset(self.devices_status)))

    def __eq__(self, other):
        if not isinstance(other, type(self)): return NotImplemented
        return self.occupied_coordinates == other.occupied_coordinates \
               and self.targets_hit == other.targets_hit\
               and set(self.devices_status) == set(other.devices_status)

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
                #yield ("move", current_name, current_coordinates, new_coordinates)

        if current_coordinates[1] < grid_size - 1:
            new_coordinates = (current_coordinates[0], current_coordinates[1] + 1, current_coordinates[2])
            if new_coordinates not in occupied_coordinates:
                possible_movements_set.add(("move", current_name, current_coordinates, new_coordinates))
                #yield ("move", current_name, current_coordinates, new_coordinates)

        if current_coordinates[2] < grid_size - 1:
            new_coordinates = (current_coordinates[0], current_coordinates[1], current_coordinates[2] + 1)
            if new_coordinates not in occupied_coordinates:
                possible_movements_set.add(("move", current_name, current_coordinates, new_coordinates))
                #yield ("move", current_name, current_coordinates, new_coordinates)

        if current_coordinates[0] > 0:
            new_coordinates = (current_coordinates[0] - 1, current_coordinates[1], current_coordinates[2])
            if new_coordinates not in occupied_coordinates:
                possible_movements_set.add(("move", current_name, current_coordinates, new_coordinates))
                #yield ("move", current_name, current_coordinates, new_coordinates)

        if current_coordinates[1] > 0:
            new_coordinates = (current_coordinates[0], current_coordinates[1] - 1, current_coordinates[2])
            if new_coordinates not in occupied_coordinates:
                possible_movements_set.add(("move", current_name, current_coordinates, new_coordinates))
                #yield ("move", current_name, current_coordinates, new_coordinates)

        if current_coordinates[2] > 0:
            new_coordinates = (current_coordinates[0], current_coordinates[1], current_coordinates[2] - 1)
            if new_coordinates not in occupied_coordinates:
                possible_movements_set.add(("move", current_name, current_coordinates, new_coordinates))
                #yield ("move", current_name, current_coordinates, new_coordinates)

        return possible_movements_set

    @staticmethod
    def get_possible_targets(current_spaceship, targets_dict, calibration_targets_dict):
        current_ship_coordinates = current_spaceship.coordinates
        current_ship_name = current_spaceship.name
        possible_targets_set = set()
        possible_targets_dict = {}

        for current_target in targets_dict:#[coordinate]:[device]
            is_straight_line = UtilsActions.check_straight_line(current_ship_coordinates, current_target)
            if is_straight_line:
                if is_straight_line[0] not in possible_targets_dict:
                    possible_targets_dict[is_straight_line[0]] = (is_straight_line[1], current_target)
                else:
                    if is_straight_line[1] < possible_targets_dict[is_straight_line[0]][0]:
                        possible_targets_dict[is_straight_line[0]] = (is_straight_line[1], current_target)

        for current_calibration_target in calibration_targets_dict: #[device]:[coordinate]
            current_target = calibration_targets_dict[current_calibration_target]
            is_straight_line = UtilsActions.check_straight_line(current_ship_coordinates, current_target)
            if is_straight_line:
                if is_straight_line[0] not in possible_targets_dict:
                    possible_targets_dict[is_straight_line[0]] = (is_straight_line[1], current_target)
                else:
                    if is_straight_line[1] < possible_targets_dict[is_straight_line[0]][0]:
                        possible_targets_dict[is_straight_line[0]] = (is_straight_line[1], current_target)

        for current_key in possible_targets_dict:
            current_coordinate = possible_targets_dict[current_key][1]
            if current_coordinate in targets_dict:
                for current_target_device in targets_dict[current_coordinate]:
                    if current_spaceship.check_ready_fire(current_target_device):
                        possible_targets_set.add(("use", current_ship_name, current_target_device, current_coordinate))
                        #yield ("use", current_ship_name, current_target_device, current_coordinate)
                        break
            else:
                for current_target_device, device_coords in calibration_targets_dict.items():
                    if device_coords == current_coordinate:
                        if current_spaceship.check_ready_calibrate(current_target_device):
                            possible_targets_set.add(("calibrate", current_ship_name, current_target_device, current_coordinate))
                            #yield ("calibrate", current_ship_name, current_target_device, current_coordinate)
                            break
                        elif current_spaceship.check_ready_turnon(current_target_device):
                            possible_targets_set.add(("turn_on", current_ship_name, current_target_device))
                            #yield ("turn_on", current_ship_name, current_target_device)
                            break

        return possible_targets_set

    @staticmethod
    def check_straight_line(tuple_coordinate1, tuple_coordinate2):
        dx = tuple_coordinate2[0] - tuple_coordinate1[0]
        dy = tuple_coordinate2[1] - tuple_coordinate1[1]
        dz = tuple_coordinate2[2] - tuple_coordinate1[2]

        if dx == 0 and dy == 0:
            return ('dz', dz) if dz > 0  else ('-dz', -dz)

        if dx == 0 and dz == 0:
            return ('dy', dy) if dy > 0 else ('-dy', -dy)

        if dy == 0 and dz == 0:
            return ('dx', dx) if dx > 0 else ('-dx', -dx)

        return None

class UtilsUpdate():
    @staticmethod
    def distribute_packet(action, spaceships_dictionary, targets_dictionary, state):
        if action[0] == 'move':
            UtilsUpdate.update_move_action(spaceships_dictionary[action[1]], action, state)
        elif action[0] == 'turn_on':
            UtilsUpdate.update_turnon_action(spaceships_dictionary[action[1]], action, state)
        elif action[0] == 'calibrate':
            UtilsUpdate.update_calibrate_action(spaceships_dictionary[action[1]], action, state)
        elif action[0] == 'use':
            UtilsUpdate.update_use_action(spaceships_dictionary[action[1]], action, targets_dictionary, state)
        else:
            print("DELETE ME: DUDE COME ON...")

    @staticmethod
    def update_move_action(spaceship_object, move_action, state):
        spaceship_old_identifier = spaceship_object.get_spaceship_identifier()
        spaceship_object.coordinates = move_action[3]
        state.remove_spaceship_occupied_coordinate(spaceship_old_identifier)
        state.add_spaceship_occupied_coordinate(spaceship_object.get_spaceship_identifier())

    @staticmethod
    def update_turnon_action(spaceship_object, turnon_action, state):
        value_to_remove = spaceship_object.turn_off_devices()
        value_to_add = spaceship_object.turn_on_device(turnon_action[2])
        if value_to_remove:
            state.remove_device_status(value_to_remove)
        state.add_device_status(value_to_add)

    @staticmethod
    def update_calibrate_action(spaceship_object, calibrate_action, state):
        value_to_remove, value_to_add = spaceship_object.calibrate_device(calibrate_action[2])
        if value_to_remove:
            state.remove_device_status(value_to_remove)
        state.add_device_status(value_to_add)

    @staticmethod
    def update_use_action(spaceship_object, use_action, targets_dictionary, state):
        current_device = use_action[2]
        current_target = use_action[3]
        targets_dictionary[current_target] = tuple(
            device for device in targets_dictionary[current_target] if device != current_device)
        state.add_target_hit((current_target, current_device))

class Spaceship():
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
        else:
            print("DELETE ME: CAN'T BE HERE.")
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
        # for device in self.devices_onoff:
        #     if self.devices_onoff[device] != 0:
        #         if self.devices_calibration[device] != 0:
        #             return (self.name, device, 1, 1)
        #         else:
        #             return (self.name, device, 1, 0)
        # return None

    def get_spaceship_identifier(self):
        return (self.coordinates+(self.name,))

class Overview():
    def __init__(self, grid_size):
        self.grid_size = grid_size
        self.state = State()
        self.spaceships = {} # [spaceship_name] : spaceship_object
        self.targets_dict = {} # [target_coordinate] : target_devices
        self.calibration_targets_dict = {} # [device_name] : target_coordinates
        self.total_number_of_hits = 0

    def set_spaceship_cells(self, ship_names, ship_initial_coordinates, ship_devices):
        for current_spaceship_name in ship_names:
            current_spaceship_coordinates = ship_initial_coordinates[current_spaceship_name]
            current_spaceship_devices = ship_devices[current_spaceship_name]
            created_ship = Spaceship(current_spaceship_coordinates, current_spaceship_name, current_spaceship_devices)
            self.spaceships[current_spaceship_name] = created_ship
            self.state.add_occupied_coordinate(created_ship.get_spaceship_identifier())

    def set_targets_cells(self, dict_coordinate_devices):
        self.targets_dict = dict_coordinate_devices
        [self.state.add_occupied_coordinate(current_coordinates) for current_coordinates in dict_coordinate_devices]
        self.total_number_of_hits = sum(len(tuple_of_devices) for tuple_of_devices in dict_coordinate_devices.values())

    def set_calibration_targets_cells(self, dict_devices_coordinates):
        self.calibration_targets_dict = dict_devices_coordinates
        [self.state.add_occupied_coordinate(dict_devices_coordinates[current_device]) for current_device in
         dict_devices_coordinates]

    def goal_test(self):
        if len(self.state.targets_hit) < self.total_number_of_hits:
            return False
        return True

    def get_possible_actions(self):
        possible_actions_set = set()
        for current_spaceship in self.spaceships.values():
            possible_actions_set.update(
               UtilsActions.get_possible_movements(current_spaceship, self.state.occupied_coordinates,
                                                   self.grid_size))
            possible_actions_set.update(
               UtilsActions.get_possible_targets(current_spaceship, self.targets_dict,
                                                   self.calibration_targets_dict))

        for current_action in possible_actions_set:
            yield current_action

    def update_action(self, action):
        UtilsUpdate.distribute_packet(action, self.spaceships, self.targets_dict, self.state)

    def __hash__(self):
        return hash((self.state))

    def __eq__(self, other):
        if not isinstance(other, type(self)):
            print("DELETE ME: WHY ARE YOU HERE?")
        is_equal = self.state == other.state
        return is_equal

class OverviewOld():
    def __init__(self, grid_size):
        self.grid_size = grid_size
        self.occupied_coordinates = set()
        self.spaceships = {} # Contains Spaceship objects
        self.targets_dict = None
        self.calibration_targets_dict = None
        self.hit_targets = set()

    def get_possible_actions(self):
        possible_actions_set = set()
        for current_spaceship in self.spaceships.values():
            possible_actions_set.update(
                UtilsActions.get_possible_movements(current_spaceship, self.occupied_coordinates,
                                                    self.grid_size))
            possible_actions_set.update(
                UtilsActions.get_possible_targets(current_spaceship, self.targets_dict,
                                                    self.calibration_targets_dict))
        for current_action in possible_actions_set:
            yield current_action

    def update_move_action(self, move_action):
        current_ship = self.spaceships[move_action[1]]
        current_ship.coordinates = move_action[3]
        self.occupied_coordinates.remove(move_action[2])
        self.occupied_coordinates.add(move_action[3])

    def update_turnon_action(self, turnon_action):
        current_ship = self.spaceships[turnon_action[1]]
        current_ship.turn_on_device(turnon_action[2])

    def update_calibrate_action(self, calibrate_action):
        current_ship = self.spaceships[calibrate_action[1]]
        current_ship.calibrate_device(calibrate_action[2])

    def update_use_action(self, use_action):
        current_ship = self.spaceships[use_action[1]]
        current_device = use_action[2]
        current_target = use_action[3]
        self.targets_dict[current_target] = tuple(
            device for device in self.targets_dict[current_target] if device != current_device)
        self.hit_targets.add((current_target, current_device))

    def add_occupied(self, coordinates):
        self.occupied_coordinates.add(coordinates)

    def goal_test(self):
        if self.targets_dict:
            return False
        return True

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
            self.spaceships[ship_name] = created_ship
            self.add_occupied(created_ship.coordinates)
            return created_ship

        # Add Spaceships coordinates to Occupied Coordinates Attribute 'self.occupied_coordinates'
        # and save Spaceship Object
        for current_name in ship_names:
            map_spaceships(ship_initial_coordinates[current_name], current_name, ship_devices[current_name])

class SpaceshipProblem(search.Problem):
    """This class implements a spaceship problem"""
    def __init__(self, initial):
        """Don't forget to set the goal or implement the goal test
        You should change the initial to your own representation"""
        self.initialize = None
        self.state = self.initialize
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
        return state.get_possible_actions()

    def result(self, state, action):
        """Return the state that results from executing the given
        action in the given state. The action must be one of
        self.actions(state)."""
        duplicate_state = deepcopy(state)
        duplicate_state.update_action(action)
        return duplicate_state

    def goal_test(self, state):
        """ Given a state, checks if this is the goal state, compares to the created goal state"""
        return state.goal_test()

    def h(self, node):
        """ This is the heuristic. It gets a node (not a state,
        state can be accessed via node.state)
        and returns a goal distance estimate"""
        print("Trying to access...")

    """Feel free to add your own functions"""

def create_spaceship_problem(problem, goal):
 
    return SpaceshipProblem(problem)

