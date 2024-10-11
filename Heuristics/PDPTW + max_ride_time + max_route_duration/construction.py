import copy
import math
import random
import read_data
import time
from tests import check_time_windows as check_time_windows2

filename = "../../Dataset/Instances/10_2.xlsx"

(num_clients, num_companies, num_vehicles, max_capacity, time_horizon, max_route_duration, max_ride_time_client,
 source, sink, vehicles, all_points, points_no_depots, pickup_points, delivery_points, set1, set2, distance,
 cost, time, service_time, demand, earliest_time, latest_time) = read_data.read_file(filename)


def update_delivery_candidates(route):
    delivery_candidates = []
    for i in range(1, len(route) - 1):
        if route[i] in pickup_points and (route[i] + num_clients) not in route:
            delivery_candidates.append(route[i] + num_clients)
    random.shuffle(delivery_candidates)
    return delivery_candidates
def check_route_capacity(route):
    capacity = 0
    for element in route:
        capacity += demand[element]
        if capacity > max_capacity:
            return False
    return True
def route_distance(route):
    total_distance = 0
    for i in range(len(route) - 1):
        current_node = route[i]
        next_node = route[i + 1]
        total_distance += distance[current_node, next_node]
    return total_distance
def update_arrival_times(route, vertex, arrival_time_dictionary):
    arrival_time_updated = copy.deepcopy(arrival_time_dictionary)
    for index in range(route.index(vertex), len(route) - 1):
        selected_vertex = route[index]
        previous_vertex = route[index - 1]
        arrival_time_updated[selected_vertex] = max(arrival_time_updated[previous_vertex] + service_time[previous_vertex] + time[previous_vertex, selected_vertex],
                                                       earliest_time[selected_vertex])
    return arrival_time_updated
def check_time_windows(vertex, route, position, arrival_time_dictionary):
    for index in range(position, len(route) - 1):
        seleceted_vertex = route[index]
        if arrival_time_dictionary[seleceted_vertex] < earliest_time[seleceted_vertex] or arrival_time_dictionary[seleceted_vertex] > latest_time[seleceted_vertex]:
            # print(f"    Arrival time = {arrival_time_dictionary[seleceted_vertex]} tw = [{earliest_time[seleceted_vertex]}, {latest_time[seleceted_vertex]}]")
            return False
    return True
def check_route_duration(route, arrival_time):
    duration = arrival_time[route[len(route) - 2]] + time[route[len(route) - 2], sink]
    if duration > max_route_duration:
        return False
    return True
def check_ride_times(route, arrival_time_dictionary, pickup_points, max_ride_time_client, num_clients):
    for client in route:
        if client in pickup_points:
            if client + num_clients in route:
                corresponding_delivery_vertex = client + num_clients
                t1 = arrival_time_dictionary[corresponding_delivery_vertex]
                t2 = arrival_time_dictionary[client] + service_time[client]
                ride_time = t1 - t2
                if ride_time > max_ride_time_client:
                    return False
    return True
def get_pickup_positions(candidates, route, arrival_time):

    min_dist = math.inf
    distance = {}

    for pickup_vertex in candidates:
        for position in range(1, len(route)):
            route.insert(position, pickup_vertex)
            # Update all arrivals time after insertion
            arrival_time_updated = update_arrival_times(route, pickup_vertex, arrival_time)

            # check for each vertex that TW condition is met
            if (check_time_windows(pickup_vertex, route, position, arrival_time_updated) and check_route_capacity(route)
                    and check_route_duration(route, arrival_time_updated)):
                distance[pickup_vertex, position] = route_distance(route)
            route.remove(pickup_vertex)

    return distance
def get_delivery_positions_vertex(vertex, route, arrival_time):
    min_dist = math.inf
    distance = {}
    corresponding_pickup_vertex = vertex - num_clients
    pickup_position = route.index(corresponding_pickup_vertex)

    for position in range(pickup_position, len(route)):
        route.insert(position, vertex)
        if position > pickup_position:
            # Update all arrivals time after insertion
            arrival_time_updated = update_arrival_times(route, vertex, arrival_time)
            # check for each vertex that TW, capacity, duration, ride times are met
            if (check_time_windows(vertex, route, position, arrival_time_updated) and check_route_capacity(route)
                    and check_route_duration(route, arrival_time_updated)
                    and check_ride_times(route, arrival_time_updated, pickup_points, max_ride_time_client,num_clients)):
                distance[position] = route_distance(route)

        route.remove(vertex)
    return distance
def check_feasibility(route, candidates, arrival_time):
    for vertex in route:
        if vertex != sink and vertex in pickup_points:
            if arrival_time[vertex] < earliest_time[vertex] or arrival_time[vertex] > latest_time[vertex]:
                index = route.index(vertex)
                route.remove(vertex)
                # print(f"SPECIAL REMOVAL (TW) {vertex}")
                candidates.append(vertex)
                del arrival_time[vertex]
                if vertex + num_clients in route:
                    route.remove(vertex + num_clients)
                    del arrival_time[vertex + num_clients]
                arrival_time = update_arrival_times(route, route[index], arrival_time)
                check_feasibility(route, candidates, arrival_time)
        elif vertex != sink and vertex in delivery_points:
            if arrival_time[vertex] < earliest_time[vertex] or arrival_time[vertex] > latest_time[vertex]:
                index = route.index(vertex - num_clients)
                route.remove(vertex)
                route.remove(vertex - num_clients)
                # print(f"SPECIAL REMOVAL (TW) {vertex} e {vertex - num_clients}")
                candidates.append(vertex - num_clients)
                del arrival_time[vertex]
                del arrival_time[vertex - num_clients]
                arrival_time = update_arrival_times(route, route[index], arrival_time)
                check_feasibility(route, candidates, arrival_time)

    for vertex in route:
        if vertex != sink and vertex in pickup_points:
            if vertex + num_clients in route:
                t1 = arrival_time[vertex + num_clients]
                t2 = arrival_time[vertex] + service_time[vertex]
                ride_time = t1 - t2
                if ride_time > max_ride_time_client:
                    index = route.index(vertex)
                    route.remove(vertex)
                    route.remove(vertex + num_clients)
                    # print(f"SPECIAL REMOVAL (ride time) {vertex} e {vertex + num_clients}")
                    candidates.append(vertex)
                    del arrival_time[vertex]
                    del arrival_time[vertex + num_clients]
                    arrival_time = update_arrival_times(route, route[index], arrival_time)
                    check_feasibility(route, candidates, arrival_time)
def get_delivery_positions(delivery_candidates, route, arrival_time):
    min_dist = math.inf
    distance = {}

    for delivery_vertex in delivery_candidates:
        corresponding_pickup_vertex = delivery_vertex - num_clients
        pickup_position = route.index(corresponding_pickup_vertex)

        for position in range(pickup_position, len(route)):
            route.insert(position, delivery_vertex)
            if position > pickup_position:
                # Update all arrivals time after insertion
                arrival_time_updated = update_arrival_times(route, delivery_vertex, arrival_time)
                # check for each vertex that TW is respected
                if (check_time_windows(delivery_vertex, route, position, arrival_time_updated) and check_route_capacity(route)
                        and check_route_duration(route, arrival_time_updated)
                        and check_ride_times(route, arrival_time_updated, pickup_points, max_ride_time_client, num_clients)):
                    distance[delivery_vertex, position] = route_distance(route)
            route.remove(delivery_vertex)
    return distance

# CONSTRUCTIVE HEURISTICS
def closest_neighbor():
    arrival_time = {}
    arrival_time[source] = 0
    routes = []
    candidates = copy.deepcopy(pickup_points)
    candidates_previous_iteration = []

    routes.append([source, sink])

    while len(candidates) != 0:

        if len(candidates) != 0 and candidates_previous_iteration == candidates:
            new_route = [source, sink]
            routes.append(new_route)

            if len(routes) != 1 and routes[len(routes) - 2] == [source, sink]:
                print(f"FAILED CONSTRUCTION. Try again")
                return closest_neighbor()

        for route_number in range(len(routes)):
            selected_route = routes[route_number]

            # Pickup Vertexes insertion
            while check_route_capacity(selected_route) and len(candidates) != 0:
                distance = get_pickup_positions(candidates, selected_route, arrival_time)

                if len(distance) != 0:

                    sorted_distances = sorted(distance.items(), key=lambda item: item[1])
                    # Get the first (vertex, position) tuple and its distance from sorted_distances
                    (vertex, position), dist = sorted_distances[0]
                    # Insert the vertex into the selected route at the specified position
                    selected_route.insert(position, vertex)
                    # Remove the vertex from the list of candidates
                    candidates.remove(vertex)
                    # Update the arrival time and other related values
                    arrival_time = update_arrival_times(selected_route, vertex, arrival_time)

                else:
                    # Non posso inserire vertici pickup, essco dal loop e inizio a inserire i vertici delivery
                    break

            # Delivery vertexes insertion
            delivery_candidates = update_delivery_candidates(selected_route)

            while len(delivery_candidates) != 0:
                distance = get_delivery_positions(delivery_candidates, selected_route, arrival_time)

                if len(distance) != 0:

                    sorted_distances = sorted(distance.items(), key=lambda item: item[1])
                    # Get the first (vertex, position) tuple and its distance from sorted_distances
                    (vertex, position), dist = sorted_distances[0]
                    # Insert the vertex into the selected route at the specified position
                    selected_route.insert(position, vertex)
                    # Update arrival time and delivery candidates
                    arrival_time = update_arrival_times(selected_route, vertex, arrival_time)
                    delivery_candidates = update_delivery_candidates(selected_route)

                else:
                    # No delivery points to add or no positions avalable. Remove pickup points without delivery
                    # print(f"NO delivery points to insert")
                    for vertex in list(selected_route):
                        if vertex in selected_route and vertex in pickup_points and vertex + num_clients not in selected_route:
                            index = selected_route.index(vertex)
                            selected_route.remove(vertex)
                            candidates.append(vertex)
                            del arrival_time[vertex]
                            # print(f"Removed {vertex}: {selected_route}")
                            # print(f"DEB selected route {selected_route}")
                            arrival_time = update_arrival_times(selected_route, selected_route[index], arrival_time)
                            check_feasibility(selected_route, candidates, arrival_time)
                            candidates.sort()
                            delivery_candidates = update_delivery_candidates(selected_route)

        candidates_previous_iteration = copy.deepcopy(candidates)
        candidates_previous_iteration.sort()


    print(f"SOLUTION:")
    total_distance = 0
    route_duration = {}
    for route in routes:
        print(f"Route {route}")
        distance = route_distance(route)
        total_distance += distance
        print(f"Route distance = {round(distance, 3)} km")
        for vertex in route:
            if vertex != sink:
                print(f"       Arrival time vertex {vertex} = {arrival_time[vertex]}")
        route_duration[routes.index(route)] = arrival_time[route[len(route) - 2]] + time[route[len(route) - 2], sink]
    print(f"Routes total durations: {route_duration} (max duration {max_route_duration}")
    print(f"TOTAL SOLUTION COST = {total_distance}")

    return routes, arrival_time, route_duration, total_distance
def construction_random_delivery():
    arrival_time = {}
    arrival_time[source] = 0
    routes = []
    candidates = copy.deepcopy(pickup_points)
    candidates_previous_iteration = []

    routes.append([source, sink])

    while len(candidates) != 0:

        if len(candidates) != 0 and candidates_previous_iteration == candidates:
            new_route = [source, sink]
            routes.append(new_route)

        for route_number in range(len(routes)):
            selected_route = routes[route_number]

            # Pickup Vertexes insertion
            while check_route_capacity(selected_route) and len(candidates) != 0:
                distance = get_pickup_positions(candidates, selected_route, arrival_time)

                if len(distance) != 0:

                    sorted_distances = sorted(distance.items(), key=lambda item: item[1])
                    # Get the first (vertex, position) tuple and its distance from sorted_distances
                    (vertex, position), dist = sorted_distances[0]
                    # Insert the vertex into the selected route at the specified position
                    selected_route.insert(position, vertex)
                    # Remove the vertex from the list of candidates
                    candidates.remove(vertex)
                    # Update the arrival time and other related values
                    arrival_time = update_arrival_times(selected_route, vertex, arrival_time)

                else:
                    # Non posso inserire vertici pickup, essco dal loop e inizio a inserire i vertici delivery
                    break

            # Delivery vertexes insertion
            delivery_candidates = update_delivery_candidates(selected_route)

            while len(delivery_candidates) != 0:
                vertex = random.choice(delivery_candidates)
                distance = get_delivery_positions_vertex(vertex, selected_route, arrival_time)

                if len(distance) != 0:

                    sorted_distances = sorted(distance.items(), key=lambda item: item[1])
                    # Get the first (position, dist) from the sorted list
                    position, dist = sorted_distances[0]
                    # Insert the vertex into the selected route at the specified position
                    selected_route.insert(position, vertex)
                    # Update the arrival time and delivery candidates
                    arrival_time = update_arrival_times(selected_route, vertex, arrival_time)
                    delivery_candidates = update_delivery_candidates(selected_route)

                else:
                    # print(f"NO positions to insert {vertex}, deleting also {vertex - num_clients}")
                    index = selected_route.index(vertex - num_clients)
                    selected_route.remove(vertex - num_clients)
                    candidates.append(vertex - num_clients)
                    del arrival_time[vertex - num_clients]
                    # print(f"Removed {vertex - num_clients}: {selected_route}")
                    arrival_time = update_arrival_times(selected_route, selected_route[index], arrival_time)
                    check_feasibility(selected_route, candidates, arrival_time)
                    candidates.sort()
                    delivery_candidates = update_delivery_candidates(selected_route)

        candidates_previous_iteration = copy.deepcopy(candidates)
        candidates_previous_iteration.sort()


    print(f"SOLUTION:")
    total_distance = 0
    route_duration = {}
    for route in routes:
        print(f"Route {route}")
        distance = route_distance(route)
        total_distance += distance
        print(f"Route distance = {round(distance, 3)} km")
        for vertex in route:
            if vertex != sink:
                print(f"       Arrival time vertex {vertex} = {arrival_time[vertex]}")
        route_duration[routes.index(route)] = arrival_time[route[len(route) - 2]] + time[route[len(route) - 2], sink]
    print(f"Routes total durations: {route_duration} (max duration {max_route_duration}")
    print(f"TOTAL SOLUTION COST = {total_distance}")

    return routes, arrival_time, route_duration, total_distance

def construction_wheighted_random_selection():
    arrival_time = {}
    arrival_time[source] = 0
    routes = []
    candidates = copy.deepcopy(pickup_points)
    candidates_previous_iteration = []

    routes.append([source, sink])

    while len(candidates) != 0:


        if len(candidates) != 0 and candidates_previous_iteration == candidates:
            new_route = [source, sink]
            routes.append(new_route)

        for route_number in range(len(routes)):
            selected_route = routes[route_number]

            # Pickup Vertexes insertion
            while check_route_capacity(selected_route) and len(candidates) != 0:
                distance = get_pickup_positions(candidates, selected_route, arrival_time)

                if len(distance) != 0:

                    keys = list(distance.keys())
                    weights = [1 / (distance[key] ** 2) for key in keys]
                    random_choice = random.choices(keys, weights=weights, k=1)[0]
                    print("Randomly selected (vertex, position):", random_choice)
                    vertex = random_choice[0]
                    position = random_choice[1]
                    # Insert the vertex into the selected route at the specified position
                    selected_route.insert(position, vertex)
                    # Remove the vertex from the list of candidates
                    candidates.remove(vertex)
                    # Update the arrival time and other related values
                    arrival_time = update_arrival_times(selected_route, vertex, arrival_time)

                else:
                    # Non posso inserire vertici pickup, essco dal loop e inizio a inserire i vertici delivery
                    break

            # Delivery vertexes insertion
            delivery_candidates = update_delivery_candidates(selected_route)

            while len(delivery_candidates) != 0:
                distance = get_delivery_positions(delivery_candidates, selected_route, arrival_time)

                if len(distance) != 0:

                    keys = list(distance.keys())
                    weights = [1 / (distance[key] ** 2) for key in keys]
                    random_choice = random.choices(keys, weights=weights, k=1)[0]
                    print("Randomly selected (vertex, position):", random_choice)
                    vertex = random_choice[0]
                    position = random_choice[1]
                    # Insert the vertex into the selected route at the specified position
                    selected_route.insert(position, vertex)
                    # Update the arrival time and other related values
                    arrival_time = update_arrival_times(selected_route, vertex, arrival_time)
                    delivery_candidates = update_delivery_candidates(selected_route)

                else:
                    # No delivery points to add and no positions avalable.
                    print(f"NO delivery points to insert, removing unpaired pickups")
                    for vertex in list(selected_route):
                        if vertex in selected_route and vertex in pickup_points and vertex + num_clients not in selected_route:
                            index = selected_route.index(vertex)
                            selected_route.remove(vertex)
                            candidates.append(vertex)
                            del arrival_time[vertex]
                            print(f"Removed {vertex}: {selected_route}")
                            print(f"DEB selected route {selected_route}")
                            arrival_time = update_arrival_times(selected_route, selected_route[index], arrival_time)
                            check_feasibility(selected_route, candidates, arrival_time)
                            candidates.sort()
                            delivery_candidates = update_delivery_candidates(selected_route)


        candidates_previous_iteration = copy.deepcopy(candidates)
        candidates_previous_iteration.sort()

    print(f"SOLUTION:")
    total_distance = 0
    route_duration = {}
    for route in routes:
        print(f"Route {route}")
        distance = route_distance(route)
        total_distance += distance
        print(f"Route distance = {round(distance, 3)} km")
        for vertex in route:
            if vertex != sink:
                print(f"       Arrival time vertex {vertex} = {arrival_time[vertex]}")
        route_duration[routes.index(route)] = arrival_time[route[len(route) - 2]] + time[route[len(route) - 2], sink]
    print(f"Routes total durations: {route_duration} (max duration {max_route_duration}")
    print(f"TOTAL SOLUTION COST = {total_distance}")

    return routes, arrival_time, route_duration, total_distance

# LOCAL SEARCH
def get_pickup_route_positions(vertex, routes, arrival_time):
    min_dist = math.inf
    distance = {}

    for route in routes:
        for position in range(1, len(route)):
            route.insert(position, vertex)
            # Update all arrivals time after insertion
            arrival_time_updated = update_arrival_times(route, vertex, arrival_time)
            # check for each vertex that TW, capacity, duration, ride times are met
            if (check_time_windows(vertex, route, position, arrival_time_updated) and check_route_capacity(route)):
                route_number = routes.index(route)
                distance[route_number, position] = route_distance(route)

            route.remove(vertex)
    return distance
def relocation(routes, arrival_time):
    """
        Relocation of a random couple pickup-delivery
    """

    print("RELOCATION START")
    # print(f"input ROUTES {routes}")
    initial_routes = copy.deepcopy(routes)
    initial_arrival_time = copy.deepcopy(arrival_time)

    random_vertex = random.choice(pickup_points)
    # print(f"Random point {random_vertex}")
    for route in routes:
        if random_vertex in route:
            # print(f"Route {routes.index(route)} prima di rimuovere random point: {route}")
            route.remove(random_vertex)
            route.remove(random_vertex + num_clients)
            # print(f"Removed {random_vertex} and {random_vertex + num_clients}")
            # print(f"Route dopo rimuovere random point {route}")
    # print(f"Ricolloco {random_vertex} e {random_vertex + num_clients}")

    pickup_distances = get_pickup_route_positions(random_vertex, routes, arrival_time)
    sorted_pickup_distances = sorted(pickup_distances.items(), key=lambda item: item[1])
    if len(pickup_distances) != 0:
        # Iterate through the sorted (vertex, position) pairs
        for (route_number, position), dist in sorted_pickup_distances:
            # print(f"Pickup vertex {random_vertex} relocated in route {route_number} in position {position}, try delovery")
            # print(f"ROUTE PRIMA {routes[route_number]}")
            routes[route_number].insert(position, random_vertex)
            # print(f"ROUTE DOPO {routes[route_number]}")
            arrival_time = update_arrival_times(routes[route_number], random_vertex, arrival_time)
            # Try insert delivery
            delivery_vertex = random_vertex + num_clients
            delivery_distances = get_delivery_positions_vertex(delivery_vertex, routes[route_number], arrival_time)
            sorted_delivery_distances = sorted(delivery_distances.items(), key=lambda item: item[1])
            if len(delivery_distances) != 0:
                # Iterate through the sorted (vertex, position) pairs
                delivery_flag = False
                for (position), dist in sorted_delivery_distances:
                    # print(f"Inserting delivery vertex {delivery_vertex} at position {position}")
                    # print(f"ROUTE PRIMA {routes[route_number]}")
                    routes[route_number].insert(position, delivery_vertex)
                    # print(f"ROUTE DOPO {routes[route_number]}")
                    arrival_time = update_arrival_times(routes[route_number], delivery_vertex, arrival_time)
                    print(f"SPOSTATA LA COPPIA {random_vertex} - {delivery_vertex} nella route {route_number}/{num_vehicles}")
                    delivery_flag = True
                    break
                if delivery_flag:
                    print("RELOCATION EXECUTION FINISH")
                    for route in routes:
                        print(route)
                        for vertex in route:
                            if vertex != sink:
                                print(f"       Arrival time vertex {vertex} = {arrival_time[vertex]}")
                    break

            else:
                print(f"No delivery positions for {delivery_vertex}, removed also {random_vertex}")
                index = routes[route_number].index(random_vertex)
                routes[route_number].remove(random_vertex)
                # arrival_time = update_arrival_times(routes[route_number], routes[route_number][index], arrival_time)
                # Back to the original sol
                routes = initial_routes
                arrival_time = initial_arrival_time
                break
    else:
        # Back to the original sol
        routes = initial_routes
        arrival_time = initial_arrival_time

    for route in routes:
        if route == [source, sink]:
            routes.remove(route)

    print(f"AFTER RELOCATION SOLUTION:")
    total_distance = 0
    route_duration = {}
    for route in routes:
        print(f"Route {route}")
        distance = route_distance(route)
        total_distance += distance
        print(f"Route distance = {round(distance, 3)} km")
        # for vertex in route:
        #     if vertex != sink:
        #         print(f"       Arrival time vertex {vertex} = {arrival_time[vertex]}")
        route_duration[routes.index(route)] = arrival_time[route[len(route) - 2]] + time[route[len(route) - 2], sink]
    print(f"Routes total durations: {route_duration} (max duration {max_route_duration}")
    print(f"TOTAL SOLUTION COST = {total_distance}")

    return routes, arrival_time, route_duration, total_distance

def relocation_first_insertion(routes, arrival_time):
    """
        Relocation of a random couple pickup-delivery
    """

    print("RELOCATION START")
    # print(f"input ROUTES {routes}")
    initial_routes = copy.deepcopy(routes)
    initial_arrival_time = copy.deepcopy(arrival_time)

    random_vertex = random.choice(pickup_points)
    # print(f"Random point {random_vertex}")
    for route in routes:
        if random_vertex in route:
            # print(f"Route {routes.index(route)} prima di rimuovere random point: {route}")
            route.remove(random_vertex)
            route.remove(random_vertex + num_clients)
            # print(f"Removed {random_vertex} and {random_vertex + num_clients}")
            # print(f"Route dopo rimuovere random point {route}")
    # print(f"Ricolloco {random_vertex} e {random_vertex + num_clients}")

    pickup_distances = get_pickup_route_positions(random_vertex, routes, arrival_time)
    sorted_pickup_distances = sorted(pickup_distances.items(), key=lambda item: item[1])
    if len(pickup_distances) != 0:
        # Iterate through the sorted (vertex, position) pairs
        for (route_number, position), dist in sorted_pickup_distances:
            # print(f"Pickup vertex {random_vertex} relocated in route {route_number} in position {position}, try delovery")
            # print(f"ROUTE PRIMA {routes[route_number]}")
            routes[route_number].insert(position, random_vertex)
            # print(f"ROUTE DOPO {routes[route_number]}")
            arrival_time = update_arrival_times(routes[route_number], random_vertex, arrival_time)
            # Try insert delivery
            delivery_vertex = random_vertex + num_clients
            delivery_distances = get_delivery_positions_vertex(delivery_vertex, routes[route_number], arrival_time)
            sorted_delivery_distances = sorted(delivery_distances.items(), key=lambda item: item[1])
            if len(delivery_distances) != 0:
                # Iterate through the sorted (vertex, position) pairs
                delivery_flag = False
                for (position), dist in sorted_delivery_distances:
                    # print(f"Inserting delivery vertex {delivery_vertex} at position {position}")
                    # print(f"ROUTE PRIMA {routes[route_number]}")
                    routes[route_number].insert(position, delivery_vertex)
                    # print(f"ROUTE DOPO {routes[route_number]}")
                    arrival_time = update_arrival_times(routes[route_number], delivery_vertex, arrival_time)
                    print(f"SPOSTATA LA COPPIA {random_vertex} - {delivery_vertex} nella route {route_number}/{num_vehicles}")
                    delivery_flag = True
                    break
                if delivery_flag:
                    break

            else:
                print(f"No delivery positions for {delivery_vertex}, removed also {random_vertex}")
                index = routes[route_number].index(random_vertex)
                routes[route_number].remove(random_vertex)
                # arrival_time = update_arrival_times(routes[route_number], routes[route_number][index], arrival_time)
                # Back to the original sol
                routes = initial_routes
                arrival_time = initial_arrival_time
                break
    else:
        # Back to the original sol
        routes = initial_routes
        arrival_time = initial_arrival_time

    for route in routes:
        if route == [source, sink]:
            routes.remove(route)

    print(f"AFTER RELOCATION SOLUTION:")
    total_distance = 0
    route_duration = {}
    for route in routes:
        print(f"Route {route}")
        distance = route_distance(route)
        total_distance += distance
        print(f"Route distance = {round(distance, 3)} km")
        # for vertex in route:
        #     if vertex != sink:
        #         print(f"       Arrival time vertex {vertex} = {arrival_time[vertex]}")
        route_duration[routes.index(route)] = arrival_time[route[len(route) - 2]] + time[route[len(route) - 2], sink]
    print(f"Routes total durations: {route_duration} (max duration {max_route_duration}")
    print(f"TOTAL SOLUTION COST = {total_distance}")

    return routes, arrival_time, route_duration, total_distance
def relocation_best_insertion(routes, arrival_time, route_duration, total_distance):
    """
        Relocation of a random couple pickup-delivery
    """

    # print("RELOCATION START")
    # print(f"input ROUTES {routes}")
    initial_routes = copy.deepcopy(routes)
    initial_arrival_time = copy.deepcopy(arrival_time)
    best_sol = copy.deepcopy((routes, arrival_time, route_duration, total_distance))
    best_distance = copy.deepcopy(total_distance)

    random_vertex = random.choice(pickup_points)
    # print(f"Random point {random_vertex}")
    for route in routes:
        if random_vertex in route:
            # print(f"Route {routes.index(route)} prima di rimuovere random point: {route}")
            route.remove(random_vertex)
            route.remove(random_vertex + num_clients)
            # print(f"Removed {random_vertex} and {random_vertex + num_clients}")
            # print(f"Route dopo rimuovere random point {route}")
    # print(f"Ricolloco {random_vertex} e {random_vertex + num_clients}")

    pickup_distances = get_pickup_route_positions(random_vertex, routes, arrival_time)
    sorted_pickup_distances = sorted(pickup_distances.items(), key=lambda item: item[1])
    if len(pickup_distances) != 0:
        for (route_number, position), dist in sorted_pickup_distances:
            routes[route_number].insert(position, random_vertex)
            arrival_time = update_arrival_times(routes[route_number], random_vertex, arrival_time)
            delivery_vertex = random_vertex + num_clients
            delivery_distances = get_delivery_positions_vertex(delivery_vertex, routes[route_number], arrival_time)
            sorted_delivery_distances = sorted(delivery_distances.items(), key=lambda item: item[1])
            if len(delivery_distances) != 0:
                for (position), dist in sorted_delivery_distances:
                    routes[route_number].insert(position, delivery_vertex)
                    arrival_time = update_arrival_times(routes[route_number], delivery_vertex, arrival_time)

                    total_distance = 0
                    route_duration = {}
                    for route in routes:
                        distance = route_distance(route)
                        total_distance += distance
                        route_duration[routes.index(route)] = arrival_time[route[len(route) - 2]] + time[
                            route[len(route) - 2], sink]

                    if total_distance < best_distance:
                        best_distance = copy.deepcopy(total_distance)
                        best_sol = copy.deepcopy((routes, arrival_time, route_duration, total_distance))

                    index = routes[route_number].index(delivery_vertex)
                    routes[route_number].remove(delivery_vertex)
                    arrival_time = update_arrival_times(routes[route_number], routes[route_number][index], arrival_time)

                index = routes[route_number].index(random_vertex)
                routes[route_number].remove(random_vertex)
                arrival_time = update_arrival_times(routes[route_number], routes[route_number][index], arrival_time)
            else:
                index = routes[route_number].index(random_vertex)
                routes[route_number].remove(random_vertex)
                arrival_time = update_arrival_times(routes[route_number], routes[route_number][index], arrival_time)

    for route in routes[:]:
        if route == [source, sink]:
            routes.remove(route)

    # print(f"AFTER RELOCATION SOLUTION:")
    # total_distance = 0
    # route_duration = {}
    # for route in routes:
    #     print(f"Route {route}")
    #     distance = route_distance(route)
    #     total_distance += distance
    #     print(f"Route distance = {round(distance, 3)} km")
    #     # for vertex in route:
    #     #     if vertex != sink:
    #     #         print(f"       Arrival time vertex {vertex} = {arrival_time[vertex]}")
    #     route_duration[routes.index(route)] = arrival_time[route[len(route) - 2]] + time[route[len(route) - 2], sink]
    # print(f"Routes total durations: {route_duration} (max duration {max_route_duration}")
    # print(f"TOTAL SOLUTION COST = {total_distance}")

    return best_sol[0], best_sol[1], best_sol[2], best_sol[3]
