import search
import random
import math
from copy import deepcopy


ids = ["204657977"]

class State():
    def __init__(self):
        self.targets_hit = set()
        self.devices_status = set()

        self.occupied_coordinates = set()
        self.spaceships_occupied_identifiers = set()

    def assign_all_variables(self, targets_occupied_coordinates, spaceships_occupied_coordinates, targets_hit_set, devices_status_set):
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
                and self.targets_hit == other.targets_hit\
                and set(self.devices_status) == set(other.devices_status)

class UtilsActions():
    @staticmethod
    def get_possible_targets(current_spaceship, targets_dict, calibration_targets_dict):
        current_ship_coordinates = current_spaceship.coordinates
        current_ship_name = current_spaceship.name
        possible_targets_dict = {}
        targets_use_set = set()
        targets_turnon_set = set()
        targets_calib_set = set()

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
                        targets_use_set.add(("use", current_ship_name, current_target_device, current_coordinate))
                        #yield ("use", current_ship_name, current_target_device, current_coordinate)
                        break
            else:
                for current_target_device, device_coords in calibration_targets_dict.items():
                    if device_coords == current_coordinate:
                        if current_spaceship.check_ready_calibrate(current_target_device):
                            targets_calib_set.add(("calibrate", current_ship_name, current_target_device, current_coordinate))
                            #yield ("calibrate", current_ship_name, current_target_device, current_coordinate)
                            break
                        elif current_spaceship.check_ready_turnon(current_target_device):
                            targets_turnon_set.add(("turn_on", current_ship_name, current_target_device))
                            #yield ("turn_on", current_ship_name, current_target_device)
                            break

        return targets_use_set, targets_calib_set, targets_turnon_set

    @staticmethod
    def get_move_action_priority(current_estimate, spaceships_dict, undo_actions_dict, state, grid_size):
        current_name = current_estimate[0].name
        current_coordinates = current_estimate[0].coordinates
        distances_directions = current_estimate[2]
        for dist, dirc in distances_directions:
            new_coordinates = UtilsActions.new_coordinates_by_direction(current_coordinates, dirc)
            new_coordinates, _ = UtilsActions.coordinates_legalization(new_coordinates, state, grid_size,
                                                                                    priority=False)
            if new_coordinates:
                return ("move", current_name, current_coordinates, new_coordinates)

        for dist, dirc in distances_directions:
            new_coordinates = UtilsActions.new_coordinates_by_direction(current_coordinates, dirc)
            new_coordinates, spaceship_name = UtilsActions.coordinates_legalization(new_coordinates, state,
                                                                                    grid_size, not_in_direction=dirc,
                                                                                    priority=True,
                                                                                    undo_actions_dict=undo_actions_dict)
            if new_coordinates and spaceship_name:
                return ("move", spaceship_name, new_coordinates, new_coordinates)

        new_coordinates = UtilsActions.move_me_anywhere(current_coordinates, state, grid_size)
        if new_coordinates:
            return ("move", current_name, current_coordinates, new_coordinates)

        return None

    @staticmethod
    def coordinates_legalization(current_coordinates, state, grid_size, not_in_direction=None, undo_actions_dict=None,
                                 priority=True):
        x, y, z = current_coordinates
        grid_legalization_part_1 = x < grid_size and y < grid_size and z < grid_size
        grid_legalization_part_2 = x > 0 and y > 0 and z > 0
        if grid_legalization_part_1 and grid_legalization_part_2:
            if current_coordinates not in state.occupied_coordinates:
                return (current_coordinates, None)
            elif priority:
                for check_identifier in state.spaceships_occupied_identifiers:
                    x, y, z, spaceship_name = check_identifier
                    check_coordinates = (x, y, z)
                    if current_coordinates == check_coordinates:
                        if spaceship_name in undo_actions_dict:
                            last_action = undo_actions_dict[spaceship_name][-1]
                            coordinate_to_return_to = last_action[2]
                            final_coordinate, ship_name = UtilsActions.coordinates_legalization(
                                coordinate_to_return_to, state, grid_size, priority=False)
                            if final_coordinate:
                                return (final_coordinate, spaceship_name)

                        new_coordinates = UtilsActions.move_me_anywhere(check_coordinates, state, grid_size,
                                                                        not_in_direction)
                        if new_coordinates:
                            return (new_coordinates, spaceship_name)
                        break
            else:
                return (None, None)
        else:
            return (None, None)

    @staticmethod
    def move_me_anywhere(current_coordinates, state, grid_size, not_in_direction = None):
        possible_directions = ['dx','dy','dz', '-dx', '-dy', '-dz']
        if not_in_direction:
            possible_directions.remove(not_in_direction)
        for dirc in possible_directions:
            new_coordinates = UtilsActions.new_coordinates_by_direction(current_coordinates, dirc)
            if UtilsActions.coordinates_legalization(new_coordinates, state ,grid_size, priority = False):
                return new_coordinates
        return None

    @staticmethod
    def new_coordinates_by_direction(current_coordinates, direction):
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
        dx = tuple_coordinate2[0] - tuple_coordinate1[0]
        dy = tuple_coordinate2[1] - tuple_coordinate1[1]
        dz = tuple_coordinate2[2] - tuple_coordinate1[2]

        if dx == 0 and dy == 0:
            return ('dz', dz, 1) if dz > 0 else ('-dz', -dz, 1)

        if dx == 0 and dz == 0:
            return ('dy', dy, 1) if dy > 0 else ('-dy', -dy, 1)

        if dy == 0 and dz == 0:
            return ('dx', dx, 1) if dx > 0 else ('-dx', -dx, 1)

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
        spaceship_old_coordinates = spaceship_object.coordinates
        spaceship_old_identifier = spaceship_object.get_spaceship_identifier()
        state.remove_spaceship_occupied_coordinate(spaceship_old_coordinates, spaceship_old_identifier)
        spaceship_object.coordinates = move_action[3]
        state.add_spaceship_occupied_coordinate(spaceship_object.coordinates,
                                                spaceship_object.get_spaceship_identifier())

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
        self.devices = None
        self.spaceships = {} # [spaceship_name] : spaceship_object
        self.targets_dict = {} # [target_coordinate] : target_devices
        self.calibration_targets_dict = {} # [device_name] : target_coordinates
        self.total_number_of_hits = 0
        self.total_number_of_hits_per_device = dict()

        self.dictionary_device_priorities = dict()
        self.device_id_on_line = 0
        self.is_turned_on = 0
        self.is_calibrated = 0
        self.current_estimate_index = 0
        self.undo_actions_dict = dict() # [ship_name] : undo_action

    def set_spaceship_cells(self, ship_names, ship_initial_coordinates, ship_devices):
        for current_spaceship_name in ship_names:
            current_spaceship_coordinates = ship_initial_coordinates[current_spaceship_name]
            current_spaceship_devices = ship_devices[current_spaceship_name]
            created_ship = Spaceship(current_spaceship_coordinates, current_spaceship_name, current_spaceship_devices)
            self.spaceships[current_spaceship_name] = created_ship
            self.state.add_spaceship_occupied_coordinate(current_spaceship_coordinates, created_ship.get_spaceship_identifier())

    def set_targets_cells(self, dict_coordinate_devices):
        self.targets_dict = dict_coordinate_devices
        [self.state.add_target_occupied_coordinate(current_coordinates) for current_coordinates in dict_coordinate_devices]
        self.total_number_of_hits = sum(len(tuple_of_devices) for tuple_of_devices in dict_coordinate_devices.values())

        for current_device in self.devices:
            count_instances = 0
            for current_target_devices in self.targets_dict.values():
                if current_device in current_target_devices:
                    count_instances+=1
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

    def initialize_on_line_device(self):
        self.is_turned_on = 0
        self.is_calibrated = 0
        self.current_estimate_index = 0

    def get_new_active_weapon(self):

        for current_device in self.dictionary_device_priorities:
            if self.dictionary_device_priorities[current_device]:
                self.device_id_on_line = self.devices.index(current_device)
                self.initialize_on_line_device()
                break

    def get_possible_actions_updated(self):
        current_device = self.devices[self.device_id_on_line]
        if current_device not in self.dictionary_device_priorities:
            self.priority_calibration()

        if not self.dictionary_device_priorities[current_device]:
            if self.total_number_of_hits_per_device[current_device] == 0:
                self.priority_calibration()
                current_device = self.devices[self.device_id_on_line]

        if not self.is_calibrated:
            is_done = False
            while not is_done:
                current_estimate = self.dictionary_device_priorities[current_device][self.current_estimate_index]
                current_estimate_spaceship = current_estimate[0]
                current_estimate_spaceship_name = current_estimate_spaceship.name

                if current_estimate_spaceship_name not in self.undo_actions_dict:
                    if self.is_turned_on:
                        return (('calibrate', current_estimate_spaceship_name, current_device, self.calibration_targets_dict[current_device]), )
                    else:
                        if current_estimate[1] == 0:
                            return (('turn_on', current_estimate_spaceship_name, current_device), )
                        else:
                            move_action = UtilsActions.get_move_action_priority(current_estimate, self.spaceships,
                                                                                self.undo_actions_dict,
                                                                                self.state,
                                                                                self.grid_size)
                            if move_action:
                                return (move_action,)
                            else:
                                if self.current_estimate_index < len(self.dictionary_device_priorities[current_device]) - 1:
                                    self.current_estimate_index += 1
                                else:
                                    print("DELETE ME: FUCK OFF SERIOUSLY NOW.")
                else:
                    if len(self.undo_actions_dict[current_estimate_spaceship_name]) == 1:
                        action_to_undo = self.undo_actions_dict[current_estimate_spaceship_name][0]
                        coordinate_to_return_to = action_to_undo[2]
                        final_coordinate, ship_name = UtilsActions.coordinates_legalization(coordinate_to_return_to,
                                                                                            self.state, self.grid_size,
                                                                                            priority=True)
                        if final_coordinate:
                            return (("move", action_to_undo[1], action_to_undo[3], action_to_undo[2]), )
                    else:
                        print("DELETE ME: Seriously, this case should never happen. ")

        else:
            print("NOT IMPLEMENTED YET")
            print(BOOM)

    def get_possible_actions(self):
        actions_move_set = set()
        actions_use_set = set()
        action_calib_set = set()
        action_turnon_set = set()

        for current_spaceship in self.spaceships.values():
            actions_move_set.update(
               UtilsActions.get_possible_movements(current_spaceship, self.state.occupied_coordinates,
                                                   self.grid_size))
            temp_use, temp_calib, temp_turnon = UtilsActions.get_possible_targets(current_spaceship, self.targets_dict,
                                                                                  self.calibration_targets_dict)
            actions_use_set.update(temp_use)
            action_calib_set.update(temp_calib)
            action_turnon_set.update(temp_turnon)

        if actions_use_set:
            for current_action in actions_use_set:
                yield current_action
        elif action_calib_set:
            for current_action in action_calib_set:
                yield current_action
        elif action_turnon_set:
            for current_action in action_turnon_set:
                yield current_action
        else:
            for current_action in actions_move_set:
                yield current_action

    def get_all_distances_dict(self, specific_spaceship = None):
        all_distances_dict = dict()

        if not specific_spaceship:
            for current_spaceship in self.spaceships.values():
                current_spaceship_coordinates = current_spaceship.coordinates

                for current_target_coordinates in self.targets_dict:
                    temp_distance, temp_direction, is_straight_line = UtilsActions.check_straight_line(
                        current_spaceship_coordinates, current_target_coordinates)
                    all_distances_dict[(current_spaceship_coordinates, current_target_coordinates)] = [
                        temp_distance, temp_direction, is_straight_line]

                for temp_calib_coordinates in self.calibration_targets_dict.values():
                    temp_distance, temp_direction, is_straight_line = UtilsActions.check_straight_line(
                        current_spaceship_coordinates, temp_calib_coordinates)
                    all_distances_dict[(current_spaceship_coordinates, temp_calib_coordinates)] = [
                        temp_distance, temp_direction, is_straight_line]

        else:
            current_spaceship_coordinates = specific_spaceship.coordinates

            for current_target_coordinates in self.targets_dict:
                temp_distance, temp_direction, is_straight_line = UtilsActions.check_straight_line(
                    current_spaceship_coordinates, current_target_coordinates)
                all_distances_dict[(current_spaceship_coordinates, current_target_coordinates)] = [
                    temp_distance, temp_direction, is_straight_line]

            for temp_calib_coordinates in self.calibration_targets_dict.values():
                temp_distance, temp_direction, is_straight_line = UtilsActions.check_straight_line(
                    current_spaceship_coordinates, temp_calib_coordinates)
                all_distances_dict[(current_spaceship_coordinates, temp_calib_coordinates)] = [
                    temp_distance, temp_direction, is_straight_line]

        return all_distances_dict

    def priority_calibration(self):
        all_distances_dict = self.get_all_distances_dict()

        for current_device in self.devices:
            print("Current Priority Device: ",current_device)
            if current_device not in self.dictionary_device_priorities:
                temporary_priorities = []
                device_calibration_coordinates = self.calibration_targets_dict[current_device]
                for current_spaceship in self.spaceships.values():
                    if current_spaceship.check_device_exists(current_device):
                        current_spaceship_coordinates = current_spaceship.coordinates
                        distances, directions, is_straight_line = all_distances_dict[
                            (current_spaceship_coordinates, device_calibration_coordinates)]

                        # Checking for Targets/Calibration Targets occlusions in straight line candidate because there is
                        # no need to move. So if there's a clear line then hitting the target is free!
                        if is_straight_line:
                            min_distance = distances
                            max_distance = distances
                            found_occlusion = False
                            number_of_occlusions = 0
                            for temp_target in self.targets_dict:
                                temp_distance, temp_direction = UtilsActions.check_straight_line(
                                    current_spaceship_coordinates, temp_target)
                                if temp_direction == directions:
                                    number_of_occlusions+=1
                                    if temp_distance < min_distance:
                                        min_distance = temp_distance
                                        found_occlusion = True
                                    elif temp_distance > max_distance:
                                        max_distance = temp_distance

                            for temp_calib  in self.calibration_targets_dict.values():
                                if temp_calib != device_calibration_coordinates:
                                    temp_distance, temp_direction = UtilsActions.check_straight_line(
                                        current_spaceship_coordinates, temp_calib)
                                    if temp_direction == directions:
                                        number_of_occlusions += 1
                                        if temp_distance < min_distance:
                                            min_distance = temp_distance
                                            found_occlusion = True
                                        elif temp_distance > max_distance:
                                            max_distance = temp_distance

                            if not found_occlusion:
                                order_by = 0
                            elif max_distance == distances - 1:
                                order_by = distances + 2
                            else:
                                order_by = min_distance + number_of_occlusions * 2

                            temporary_priorities.append([current_spaceship, order_by, (distances, directions)])

                        else:
                            order_by = sum(distances) - max(distances)
                            distances_directions = sorted(zip(distances, directions), key=lambda dist: dist[0])
                            temporary_priorities.append([current_spaceship, order_by, distances_directions])

                temporary_priorities.sort(key=lambda priority: priority[1])
                self.dictionary_device_priorities[current_device] = temporary_priorities
                print(self.dictionary_device_priorities)
                strtoprint =""
                for i in self.dictionary_device_priorities[current_device]:
                    strtoprint+= (i[0].name+"\t-\t")
                print(strtoprint)
                break
        self.get_new_active_weapon()

    def update_priority_calibration(self):
        current_device = self.devices[self.device_id_on_line]
        current_estimate = self.dictionary_device_priorities[current_device][self.current_estimate_index]
        current_estimate_spaceship = current_estimate[0]
        current_spaceship_coordinates = current_estimate_spaceship.coordinates
        current_estimate_spaceship_name = current_estimate_spaceship.name
        device_calibration_coordinates =  self.calibration_targets_dict[current_device]

        distances, directions, is_straight_line = UtilsActions.check_straight_line(
            current_spaceship_coordinates, device_calibration_coordinates)

        # Checking for Targets/Calibration Targets occlusions in straight line candidate because there is
        # no need to move. So if there's a clear line then hitting the target is free!
        if is_straight_line:
            min_distance = distances
            max_distance = distances
            found_occlusion = False
            number_of_occlusions = 0
            for temp_target in self.targets_dict:
                temp_distance, temp_direction, is_target_straight = UtilsActions.check_straight_line(
                    current_spaceship_coordinates, temp_target)
                if is_target_straight:
                    if temp_direction == directions:
                        number_of_occlusions+=1
                        if temp_distance < min_distance:
                            min_distance = temp_distance
                            found_occlusion = True
                        elif temp_distance > max_distance:
                            max_distance = temp_distance

            for temp_calib  in self.calibration_targets_dict.values():
                if temp_calib != device_calibration_coordinates:
                    temp_distance, temp_direction, is_target_straight = UtilsActions.check_straight_line(
                        current_spaceship_coordinates, temp_calib)
                    if is_target_straight:
                        if temp_direction == directions:
                            number_of_occlusions += 1
                            if temp_distance < min_distance:
                                min_distance = temp_distance
                                found_occlusion = True
                            elif temp_distance > max_distance:
                                max_distance = temp_distance

            del self.dictionary_device_priorities[current_device][self.current_estimate_index]
            if not found_occlusion:
                order_by = 0
                self.dictionary_device_priorities[current_device].insert(0, [current_estimate_spaceship, order_by,
                                                                             (distances, directions)])
            else:
                if max_distance == distances - 1:
                    order_by = distances + 2
                else:
                    order_by = min_distance + number_of_occlusions * 2

                for i_index in range(len(self.dictionary_device_priorities[current_device])):
                    if order_by < self.dictionary_device_priorities[current_device][i_index][1]:
                        self.dictionary_device_priorities[current_device].insert(i_index,
                                                                                 [current_estimate_spaceship, order_by,
                                                                                  (distances, directions)])

            self.current_estimate_index = 0

        else:
            order_by = sum(distances) - max(distances)
            distances_directions = sorted(zip(distances, directions), key=lambda dist: dist[0])
            self.dictionary_device_priorities[current_device][self.current_estimate_index] = [current_estimate_spaceship, order_by,
                                                                         distances_directions]

    def update_action(self, action):
        print(action)
        UtilsUpdate.distribute_packet(action, self.spaceships, self.targets_dict, self.state)
        if action[0] == 'move':
            spaceship_name_to_move = action[1]

            current_device = self.devices[self.device_id_on_line]
            spaceship_active_name = self.dictionary_device_priorities[current_device][self.current_estimate_index][0].name

            if spaceship_name_to_move != spaceship_active_name:
                if spaceship_name_to_move in self.undo_actions_dict:
                    self.undo_actions_dict[spaceship_name_to_move].append(action)
                else:
                    self.undo_actions_dict[spaceship_name_to_move] = [action]
            else:
                self.update_priority_calibration()

        elif action[0] == 'turn_on':
            self.is_turned_on = 1
        elif action[0] == 'calibrate':
            self.is_calibrated = 1
            self.dictionary_device_priorities[action[2]] = []

    def __hash__(self):
        return hash((self.state))

    def __eq__(self, other):
        if not isinstance(other, type(self)):
            print("DELETE ME: WHY ARE YOU HERE?")
        is_equal = self.state == other.state
        return is_equal

    def __lt__(self, node):
        return self.state < node.state

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
        self.initialize.set_devices(devices)
        self.initialize.set_targets_cells(targets)


    def actions(self, state):
        """Return the actions that can be executed in the given
        state. The result would typically be a tuple, but if there are
        many actions, consider yielding them one at a time in an
        iterator, rather than building them all at once."""
        action = state.get_possible_actions_updated()
        return action

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

'''

TO DO:
Move first ship with lowest distance to initialdistance->calib->target.
then calculate again the lowest distance to next targets
Now what if there are multiple targets?

So.. ideas..
Finish all targets that have weapon x.
Then all targets that have wepaon y and so on

OK 

Read all input
Check if relative number of weapons to ships
if equal, each ship gets a weapons
else if weapons less than ships, also easy just let the furthest ship sit aside
else if weapons more than ships, now need to think




'''
