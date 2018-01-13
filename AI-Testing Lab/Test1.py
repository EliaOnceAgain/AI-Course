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
        self.space_cube_3d = [[[Space3DCell((i, j, k)) for k in range(grid_size)] for j in range(grid_size)] for i in range(grid_size)]
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

class DevicesStorage():
    def __init__(self):
        '''
        Dictionary Build
            [RunningID] : {weapon_name, number_of_instances}
        '''
        self.device = {}
        self.targets = {}

    def check_existence(self, weapon_name):
        if weapon_name in self.device.values():
            return True
        return False

    def add_new_weapon(self, weapon_name):
        '''
        Checks if a weapon already exists in dictionary, if it doesn't then add it.
        :ARGS:
            weapon_name - (string) Name of weapon to add if not in dict.
        '''
        if not self.check_existence(weapon_name):
            self.device[len(self.device)] = weapon_name

    def add_weapon_target(self, target):
        '''
        Adds Target object to
        :param target:
        :return:
        '''

    def __repr__(self):
        string_to_print = ""
        for device_id, device_data in self.device.items():
            string_to_print += ("ID: " + str(device_id) + "\tName: " + str(device_data) + "\n")
        return string_to_print


if __name__ == '__main__':


