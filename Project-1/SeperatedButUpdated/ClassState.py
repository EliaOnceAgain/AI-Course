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

    def remove_occuped_coordinate(self, occupied_coordinate_tuple):
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