import search
import random
import math
from copy import deepcopy

ids = ["204657977"]
print_all_headlines = False
print_main_headlines = False


class MyState():
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


class UtilsActions():
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
                                                                                                    not_in_direction=[dirc],
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

        move_actions_set = set()
        current_ship_name = current_estimate[0].name
        current_ship_coordinates = current_estimate[0].coordinates
        distances_directions = current_estimate[2]

        if isinstance(distances_directions[0], int):
            distances_directions = (distances_directions,)

        move_actions_set.update(
            UtilsActions.good_cop_bad_cop(current_ship_name, current_ship_coordinates, state, grid_size,
                                          distances_directions))

        new_coordinates = UtilsActions.move_me_anywhere(current_ship_coordinates, state, grid_size, main_ship=False,
                                                        not_in_direction=[row[1] for row in distances_directions])
        if new_coordinates:
            move_actions_set.add(("move", current_ship_name, current_ship_coordinates, new_coordinates))

        # new_coordinates = UtilsActions.move_me_anywhere(current_ship_coordinates, state, grid_size, main_ship=True)
        # if new_coordinates:
        #     for current_new_coordinates in new_coordinates:
        #         move_actions_set.add(("move", current_ship_name, current_ship_coordinates, current_new_coordinates))

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

        new_coordinates = UtilsActions.move_me_anywhere(current_ship_coordinates, state, grid_size, main_ship=False,
                                                        not_in_direction=[row[1] for row in distances_directions])
        if new_coordinates:
            move_actions_set.add(("move", current_ship_name, current_ship_coordinates, new_coordinates))

        # new_coordinates = UtilsActions.move_me_anywhere(current_ship_coordinates, state, grid_size, main_ship=True)
        # if new_coordinates:
        #     for current_new_coordinates in new_coordinates:
        #         move_actions_set.add(("move", current_ship_name, current_ship_coordinates, current_new_coordinates))

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
    def move_me_anywhere(current_coordinates, state, grid_size, not_in_direction=None, main_ship = False):
        if print_all_headlines:
            print(">>> Function: move_me_anywhere")

        movements_set = set()
        possible_directions = ['dx', 'dy', 'dz', '-dx', '-dy', '-dz']
        if not_in_direction:
            for current_dirc in not_in_direction:
                possible_directions.remove(current_dirc)
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


class UtilsUpdate():
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
        else: # elif action[0] == 'use':
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


class UtilsGeneral():
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


class PriorityManager():
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
        self.devices_introduced = set()

    def reset_introduced_device(self, current_device):
        if current_device in self.devices_introduced:
            self.devices_introduced.remove(current_device)

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

    def get_calib_estimate_action(self, current_estimate, current_device, as_single = False):
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

    def get_calibration_actions(self):
        if print_all_headlines or print_main_headlines:
            print(">>> Function: get_calibration_actions")

        def introduce_device(current_device):
            if current_device in self.devices_introduced:
                return False
            return True

        current_device = self.overview_obj.devices[self.overview_obj.online_device_id]

        current_estimate = self.overview_obj.dictionary_device_spaceships_priorities[current_device][
            self.overview_obj.calibration_current_estimate_index]

        if current_estimate[1] == 0:
            yield self.get_calib_estimate_action(current_estimate, current_device, as_single = True)

        if introduce_device(current_device):
            self.devices_introduced.add(current_device)
            for current_estimate_index in range(
                    len(self.overview_obj.dictionary_device_spaceships_priorities[current_device])):

                current_estimate = self.overview_obj.dictionary_device_spaceships_priorities[current_device][
                    current_estimate_index]
                current_estimate_actions_set = self.get_calib_estimate_action(current_estimate, current_device)

                self.overview_obj.calibration_current_estimate_index = current_estimate_index
                for current_action in current_estimate_actions_set:
                    yield current_action

                self.add_device_ship_deadend(current_device, current_estimate[0].name)

        else:
            current_estimate = self.overview_obj.dictionary_device_spaceships_priorities[current_device][
                self.overview_obj.calibration_current_estimate_index]
            current_estimate_actions_set = self.get_calib_estimate_action(current_estimate, current_device)

            for current_action in current_estimate_actions_set:
                yield current_action


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

    def get_current_target_priority(self, current_spaceship_coordinates, current_target_coordinates, all_distances_dict):
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

                current_estimate_actions_set = UtilsActions.get_move_action_priority_targets(current_estimate, current_estimate_spaceship, self.overview_obj.state,
                                                                     self.overview_obj.grid_size)

                self.overview_obj.use_device_current_estimate_index = current_estimate_index
                for current_action in current_estimate_actions_set:
                    yield current_action

            # Make sure 'use_device_current_estimate_index' is initialized to zero somewhere in Calib priority
            self.overview_obj.calib_priority_manager.add_device_ship_deadend(current_device, current_estimate_spaceship_name)
            self.overview_obj.calib_priority_manager.priority_calib_main()
            calibration_actions = self.overview_obj.calib_priority_manager.get_calibration_actions()
            for current_action in calibration_actions:
                yield current_action


        else:
            current_estimate = self.overview_obj.dictionary_device_targets_priorities[current_device][
                self.overview_obj.use_device_current_estimate_index]
            current_estimate_actions_set = UtilsActions.get_move_action_priority_targets(current_estimate, current_estimate_spaceship, self.overview_obj.state,
                                                                     self.overview_obj.grid_size)

            for current_action in current_estimate_actions_set:
                yield current_action


class Overview():
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

        self.heuristic_value = -1

    def calculate_heuristic_value(self):
        if self.goal_test():
            return 0

        len_dictionary_device_spaceships_priorities = len(self.dictionary_device_spaceships_priorities)

        difference_calibration = len(self.devices) - len_dictionary_device_spaceships_priorities
        difference_target = self.total_number_of_hits - len(self.state.targets_hit)

        if difference_calibration == len(self.devices):
            self.heuristic_value = 99999999999
            return self.heuristic_value



        self.heuristic_value = int(
            str(difference_target) + str(difference_calibration) + str(self.use_device_current_estimate_index) + str(
                self.calibration_current_estimate_index))

        #print(self.heuristic_value)
        return self.heuristic_value

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

    def get_possible_actions(self):
        if print_all_headlines or print_main_headlines:
            print(">>> Function: get_possible_actions")

        if not self.is_calibrated:
            return self.calib_priority_manager.get_calibration_actions()

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


class SpaceshipProblem(search.Problem):
    """This class implements a spaceship problem"""

    def __init__(self, initial):
        """Don't forget to set the goal or implement the goal test
        You should change the initial to your own representation"""
        self.initialize = None
        self.state = self.initialize
        self.unpack_problem(initial)
        search.Problem.__init__(self, initial=self.initialize)

    def unpack_problem(self, initial):
        grid_size = initial[0]  # Integer
        spaceships_names = initial[1]  # Tuple of Strings
        devices = initial[2]  # Tuple of Strings
        ships_devices = initial[3]  # Dictionary of Tuples
        calibration_targets = initial[4]  # Dictionary of Tuples
        targets = initial[5]  # Dictionary of Tuples
        initial_positions = initial[6]  # Dictionary of Tuples

        self.initialize = Overview(grid_size)
        self.initialize.set_spaceship_cells(spaceships_names, initial_positions, ships_devices)
        self.initialize.set_calibration_targets_cells(calibration_targets)
        self.initialize.set_devices(devices)
        self.initialize.set_targets_cells(targets)
        self.initialize.calculate_heuristic_value()
        self.initialize.check_active_devices()

    def actions(self, state):
        """Return the actions that can be executed in the given
        state. The result would typically be a tuple, but if there are
        many actions, consider yielding them one at a time in an
        iterator, rather than building them all at once."""
        all_possible_actions = state.get_possible_actions()
        for current_possible_action in all_possible_actions:
            yield current_possible_action

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
        return node.state.calculate_heuristic_value()


def create_spaceship_problem(problem, goal):
    return SpaceshipProblem(problem)
