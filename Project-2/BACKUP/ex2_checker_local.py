import ex21


def get_num_of_transmitters(Lazer_transm_tuple):
    [x_y_trans, x_z_tran, y_z_tran] = Lazer_transm_tuple
    num_of_transmitters = len(x_y_trans) + len(x_z_tran) + len(y_z_tran)
    return num_of_transmitters


def check_solution(problem, lazer_locations, print_single_results=False):
    controller = ex21.SpaceshipController(problem, get_num_of_transmitters(lazer_locations))
    grid_size = controller.state.grid_size

    def ex2_get_next_action(print_data=False):
        observation = get_observation()
        if print_data:
            print("Received Observation: ", observation)
        action = controller.get_next_action(observation)
        if print_data:
            print("Returned Action: ", action)
            #print()
        return action

    def get_observation():
        observations_dict = dict()

        for current_ship in controller.state.spaceships:
            current_ship_obj = controller.state.spaceships[current_ship]
            current_ship_coordinates = current_ship_obj.coordinates
            x, y, z = current_ship_coordinates

            if laser_in_coordinate(lazer_locations, current_ship_coordinates):
                observations_dict[current_ship] = -1
                continue

            count = 0

            px = None
            nx = None
            py = None
            ny = None
            pz = None
            nz = None

            if check_within_grid_range((x - 1, y, z)):
                px = (x - 1, y, z)
            if check_within_grid_range((x + 1, y, z)):
                nx = (x + 1, y, z)
            if check_within_grid_range((x, y - 1, z)):
                py = (x, y - 1, z)
            if check_within_grid_range((x, y + 1, z)):
                ny = (x, y + 1, z)
            if check_within_grid_range((x, y, z - 1)):
                pz = (x, y, z - 1)
            if check_within_grid_range((x, y, z + 1)):
                nz = (x, y, z + 1)

            if px:
                if laser_in_coordinate(lazer_locations, px):
                    count += 1
            if nx:
                if laser_in_coordinate(lazer_locations, nx):
                    count += 1
            if py:
                if laser_in_coordinate(lazer_locations, py):
                    count += 1
            if ny:
                if laser_in_coordinate(lazer_locations, ny):
                    count += 1
            if pz:
                if laser_in_coordinate(lazer_locations, pz):
                    count += 1
            if nz:
                if laser_in_coordinate(lazer_locations, nz):
                    count += 1

            if count:
                observations_dict[current_ship] = count

        return observations_dict

    def check_within_grid_range(current_coordinates):
        x, y, z = current_coordinates
        grid_legalization_part_1 = x < grid_size and y < grid_size and z < grid_size
        grid_legalization_part_2 = x >= 0 and y >= 0 and z >= 0
        return grid_legalization_part_1 and grid_legalization_part_2

    def laser_in_coordinate(lazer_locations, coordinate):
        x, y, z = coordinate
        entrance_num = 0
        for ll in lazer_locations:  # ((x, y),...), ((x, z),....), ((y, z),....)
            for l in ll:
                # print(lazer_locations)
                # print(ll)
                # print(l)
                # print()
                p1, p2 = l
                if entrance_num == 0:
                    if compare_coordinates_pleaseee(x, y, p1, p2):
                        return True
                elif entrance_num == 1:
                    if compare_coordinates_pleaseee(x, z, p1, p2):
                        return True
                elif entrance_num == 2:
                    if compare_coordinates_pleaseee(y, z, p1, p2):
                        return True
                else:
                    return WTF

            entrance_num += 1

    def compare_coordinates_pleaseee(x1, x2, p1, p2):
        if x1 == p1 and x2 == p2:
            return -1

    number_of_actions = 0
    while True:
        next_action = ex2_get_next_action(print_data=True)
        if next_action:
            number_of_actions += 1
            controller.result(next_action)
            if controller.goal_test(controller.state):
                if print_single_results:
                    print(">>> Mission Completed!")
                    print(">>> Number of Actions: ", number_of_actions)
                    print("------------------------------")
                return True

        else:
            if print_single_results:
                print(">>> Mission Failed!")
                print(">>> Number of Actions: ", number_of_actions)
                print("------------------------------")
            return None
