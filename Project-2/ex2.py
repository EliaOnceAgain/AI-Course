__author__ = 'sarah'

ids = ["204657977"]

import logic
import search
import copy
import itertools

import ex1forex2


class KB_Manager:
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

        self.explored = False
        self.explored_by = set()

        self.has_indication = False  # Remember that if unexplored and false then it's unknown
        self.safe = 0  # 1 = Safe, -1 = Fire, 0 = Unknown

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
        self.guru = KB_Manager()
        self.safe_dict = {'x': set(), 'y': set(), 'z': set()}
        self.fire_dict = {'x': set(), 'y': set(), 'z': set()}
        self.safe_but_unexplored = set()

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
                self.safe_but_unexplored.add(coordinates)

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

        state = ex1forex2.Overview(grid_size)
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
            if current_possible_action[0] == 'move':
                destination = current_possible_action[2]
                if self.grid_manager.check_destination_safety(destination):
                    yield current_possible_action
                else:
                    continue

            else:
                yield current_possible_action

    def result(self, action):
        self.state.update_action(action)

    def goal_test(self, state):
        return state.goal_test()

    def h(self, node):
        return node.state.calculate_heuristic_value()

# TODO : COMPLETE BY STUDENTS
# get observation for the current state and return next action to apply (and None if no action is applicable)
