import copy
import math
import random
import read_data
import time


from tests import check_ride_times as check_ride_times2
from tests import check_time_windows as check_time_windows2
from tests import check_route_duration as check_route_duration2

filename = "../../Dataset/Instances/100_8.xlsx.xlsx"

(num_clients, num_companies, num_vehicles, max_capacity, time_horizon, max_route_duration, max_ride_time_client,
 source, sink, vehicles, all_points, points_no_depots, pickup_points, delivery_points, set1, set2, distance,
 cost, time, service_time, demand, earliest_time, latest_time) = read_data.read_file(filename)

def load(route):
    load = 0
    for i in route:
        load += demand[i]
    return load
def get_route_duration(route, arrival_time):
    return arrival_time[route[len(route) - 2]] + time[route[len(route) - 2], sink]
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
def select_pickup_vertex(route, alpha, candidates):
    min_dist = math.inf
    max_dist = - math.inf
    for i in route:
        if i != sink:
            for j in candidates:
                if distance[i, j] < min_dist:
                    min_dist = distance[i, j]
                if distance[i, j] > max_dist:
                    max_dist = distance[i, j]
    restricted_candidate_list = []
    # print(max_dist)
    # print(min_dist)
    # print(restricted_candidate_list)
    # print(min_dist + alpha * (max_dist - min_dist))

    # print("candidates = ", candidates)
    for i in route:
        if i != sink:
            for j in candidates:
                if distance[i, j] <= min_dist + alpha * (max_dist - min_dist) and j not in restricted_candidate_list:
                    restricted_candidate_list.append(j)

    if not restricted_candidate_list:
        print("RCL is empty")
        return None
    else:
        return random.choice(restricted_candidate_list)
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
        if arrival_time_dictionary[seleceted_vertex] > latest_time[seleceted_vertex]:
            # print(f"    Arrival time = {arrival_time_dictionary[seleceted_vertex]} tw = [{earliest_time[seleceted_vertex]}, {latest_time[seleceted_vertex]}]")
            return False
    return True
def ride_time_client(client, arrival_time_dictionary):
    corresponding_delivery_vertex = client + num_clients
    t1 = arrival_time_dictionary[corresponding_delivery_vertex]
    t2 = arrival_time_dictionary[client] + service_time[client]
    return t1-t2
def get_pickup_positions(vertex, route, arrival_time):
    '''
    :return:
    '''
    min_dist = math.inf
    distance = {}

    for position in range(1, len(route)):
        route.insert(position, vertex)
        # Update all arrivals time after insertion
        arrival_time_updated = update_arrival_times(route, vertex, arrival_time)

        # check for each vertex that TW condition is met
        if check_time_windows(vertex, route, position, arrival_time_updated) and check_route_capacity(route):
            distance[position] = route_distance(route)
        route.remove(vertex)

    return distance

def check_ride_times3(route, arrival_time_dictionary, pickup_points, max_ride_time_client, num_clients, service_time):
    for client in route:
        if client in pickup_points:
            if client + num_clients in route:
                ride_time = ride_time_client(client, arrival_time_dictionary)
                if ride_time > max_ride_time_client:
                    # print(f"ride time client {client} = {ride_time} min, but MAX = {max_ride_time_client}")
                    return False
    return True
def get_delivery_positions(vertex, route, arrival_time):
    min_dist = math.inf
    distance = {}
    corresponding_pickup_vertex = vertex - num_clients
    pickup_position = route.index(corresponding_pickup_vertex)

    for position in range(1, len(route)):
        route.insert(position, vertex)
        if position > pickup_position:
            # Update all arrivals time after insertion
            arrival_time_updated = update_arrival_times(route, vertex, arrival_time)
            # check for each vertex that TW is respected
            if (check_time_windows(vertex, route, position, arrival_time_updated)
                and check_ride_times3(route, arrival_time_updated, pickup_points, max_ride_time_client, num_clients, service_time)
                    and get_route_duration(route, arrival_time_updated) <= max_route_duration):
                distance[position] = route_distance(route)
                # print(f"Ride time {ride_time_client(corresponding_pickup_vertex, arrival_time_updated)}")
        route.remove(vertex)
    return distance
def check_feasibility(route, candidates, arrival_time):
    for vertex in route:
        if vertex != sink and vertex in pickup_points:
            if arrival_time[vertex] < earliest_time[vertex] or arrival_time[vertex] > latest_time[vertex]:
            # if arrival_time[vertex] > latest_time[vertex]:
                index = route.index(vertex)
                route.remove(vertex)
                # print(f"Rimuovo {vertex}")
                candidates.append(vertex)
                del arrival_time[vertex]
                if vertex + num_clients in route:
                    route.remove(vertex + num_clients)
                    del arrival_time[vertex + num_clients]
                arrival_time = update_arrival_times(route, route[index], arrival_time)
                check_feasibility(route, candidates, arrival_time)
        elif vertex != sink and vertex in delivery_points:
            if arrival_time[vertex] < earliest_time[vertex] or arrival_time[vertex] > latest_time[vertex]:
            # if arrival_time[vertex] > latest_time[vertex]:
                index = route.index(vertex - num_clients)
                route.remove(vertex)
                route.remove(vertex - num_clients)
                # print(f"Rimuovo {vertex} e {vertex - num_clients}")
                candidates.append(vertex - num_clients)
                del arrival_time[vertex]
                del arrival_time[vertex - num_clients]
                arrival_time = update_arrival_times(route, route[index], arrival_time)
                check_feasibility(route, candidates, arrival_time)

    for vertex in route:
        if vertex != sink and vertex in pickup_points:
            if vertex + num_clients in route:
                if ride_time_client(vertex, arrival_time) > max_ride_time_client:
                    index = route.index(vertex)
                    route.remove(vertex)
                    route.remove(vertex + num_clients)
                    # print(f"Rimuovo {vertex} e {vertex + num_clients}")
                    candidates.append(vertex)
                    del arrival_time[vertex]
                    del arrival_time[vertex + num_clients]
                    arrival_time = update_arrival_times(route, route[index], arrival_time)
                    check_feasibility(route, candidates, arrival_time)
def construction(max_feasible_iter):
    """
    :param max_feasible_iter: numero massimo di iterazioni in cui si cerca di costruire una soluzione feasible
                              per il numero massimo di veicoli
                              dopo questo numero si decide di utilizzare più veicoli di quelli a disposizione
    :return:
    """
    arrival_time = {}
    arrival_time[source] = 0
    routes = []
    candidates = copy.deepcopy(pickup_points)
    candidates_previous_iteration = []
    iter_count = 0
    total_iterations = 0
    # print(arrival_time, routes, candidates, iter_count, total_iterations)

    # creo n route vuote sorce-sink dove n = numero veicoli
    for i in range(num_vehicles):
        routes.append([source, sink])

    while len(candidates) != 0:

        if candidates_previous_iteration == candidates:
            iter_count += 1
            total_iterations += 1
        else:
            iter_count = 0
        # print(f"    ITER COUNT {iter_count}")

        # Inserimento vertici pickup
        for route_number in range(len(routes)):
            # print(f"Riempio PICKUP Route {route_number}")
            selected_route = routes[route_number]

            while load(selected_route) < max_capacity and len(candidates) != 0:
                # print(f"Candidates {candidates}")
                selected_pickup = random.choice(candidates)
                # print(f"SELECTED PICKUP POINT {selected_pickup}")
                pickup_positions = get_pickup_positions(selected_pickup, selected_route, arrival_time)
                if len(pickup_positions) != 0:
                    selected_route.insert(random.choice(list(pickup_positions.keys())), selected_pickup)
                    candidates.remove(selected_pickup)
                    # print(f"    {routes[route_number]}")
                    arrival_time = update_arrival_times(selected_route, selected_pickup, arrival_time)
                    check_feasibility(selected_route, candidates, arrival_time)
                else:
                    break

            # Li inserisco nella miglior posizione
            # print(f"DELIVERIES")
            delivery_candidates = update_delivery_candidates(selected_route)
            while len(delivery_candidates) != 0:
                vertex = random.choice(delivery_candidates)
                delivery_positions = get_delivery_positions(vertex, selected_route, arrival_time)
                if len(delivery_positions) != 0:
                    selected_delivery = random.choice(list(delivery_positions.keys()))
                    selected_route.insert(selected_delivery, vertex)
                    # print(f"    {routes[route_number]}")
                    arrival_time = update_arrival_times(selected_route, vertex, arrival_time)
                    check_feasibility(selected_route, candidates, arrival_time)
                    # Update delivery candidates
                    # print(f"Delivery candidates before update {delivery_candidates}")
                    # print(f"Route before update {selected_route}")
                    delivery_candidates = update_delivery_candidates(selected_route)
                    # print(f"Delivery candidates after update {delivery_candidates}")
                    # print(f"Route after update {selected_route}")

                else:
                    # Non posso inserire il vertice delivery in nessuna posizione, quindi
                    # rimuovo il corrispondente pickup vertex e lo rimetto tra i candidati
                    corresponding_pickup_vertex = vertex - num_clients
                    index = selected_route.index(corresponding_pickup_vertex)
                    selected_route.remove(corresponding_pickup_vertex)
                    candidates.append(corresponding_pickup_vertex)
                    candidates.sort()
                    del arrival_time[corresponding_pickup_vertex]
                    # print(f"Removed {corresponding_pickup_vertex}")
                    arrival_time = update_arrival_times(selected_route, selected_route[index], arrival_time)
                    # p1 = copy.deepcopy(arrival_time)
                    # route_before = copy.deepcopy(selected_route)
                    check_feasibility(selected_route, candidates, arrival_time)
                    delivery_candidates = update_delivery_candidates(selected_route)

                    # controllo se le tw di tutta la sol sono rispettate -> se ne trovo uno non rispettato elimino la
                    # coppia di vertici e rimetto il pickup tra i candidates
                    # posos usare check_time_windows(route) del file tests.py
                    # controllo se i ride time di tuuta la sol sono rispettti -> se ne trovo uno non rispettao elimino la
                    # coppia di vertici e rimetto il pickup tra i candidates
                    # print(f"Arrival time = {arrival_time}")


        if len(candidates) != 0 and iter_count >= max_feasible_iter:
            # print(f"Creo una nuova route")
            new_route = [source, sink]
            routes.append(new_route)
            iter_count = 0

        empty_routes_counter = 0
        for route in routes:
            if route == [source, sink]:
                empty_routes_counter += 1

        if len(candidates) != 0 and len(routes) > num_vehicles and empty_routes_counter >= 3:
            # print("RECURSIVE CALL")
            return construction(max_feasible_iter)

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

def relocate_inter(routes, arrival_time, route_duration, total_distance):
    """
    The pickup and delivery vertices associated with a same request are moved from a route p1 to a route p2
    """
    extra_routes = []
    candidate_list = []

    for route_number in range(num_vehicles, len(routes)):
        extra_routes.append(routes[route_number])
        for vertex in routes[route_number]:
            if vertex in pickup_points:
                candidate_list.append(vertex)

    for candidate_vertex in candidate_list:
        for route_number in range(0, num_vehicles):
            route = routes[route_number]
            for pickup_position in range(1, len(route)):
                route.insert(pickup_position, candidate_vertex)
                # print(f"Route = {route}")
                arrival_time = update_arrival_times(route, candidate_vertex, arrival_time)
                delivery_inserted = False
                if check_route_capacity(route) and check_time_windows2(route, routes, route_duration, sink, arrival_time, earliest_time, latest_time):
                    print(f"Inserito vertice {candidate_vertex} nella route {route_number}")
                    # for element in route:
                    #     if element != sink:
                    #         print(
                    #             f"       ARRIVAL TIME DELLA ROUTE DOPO MEZZA RELOCATION {element} = {arrival_time[element]}")

                    for delivery_position in range(pickup_position + 1, len(route)):
                        delivery_vertex = candidate_vertex + num_clients
                        route.insert(delivery_position, delivery_vertex)
                        print(f"Route {route}")
                        arrival_time = update_arrival_times(route, delivery_vertex, arrival_time)
                        if (check_route_capacity(route)
                            and check_time_windows2(route, routes, route_duration, sink, arrival_time, earliest_time, latest_time)
                            and check_ride_times2(route, arrival_time, pickup_points, max_ride_time_client, num_clients, service_time)
                            and check_route_duration2(route, routes, route_duration, max_route_duration)):
                            delivery_inserted = True
                            print(f"RELOCATION: insertiscco vertici {candidate_vertex} e {delivery_vertex} nella route {route_number}")

                            # for vertex in route:
                            #     if vertex != sink:
                            #         print(f"       ARRIVAL TIME DELLA ROUTE DOPO LA RELOCATION {vertex} = {arrival_time[vertex]}")

                            for extra_route in extra_routes:
                                if candidate_vertex in extra_route:
                                    print(f"Extra route prima: {extra_route}")
                                    extra_route.remove(candidate_vertex)
                                    extra_route.remove(delivery_vertex)
                                    print(f"Extra route dopo: {extra_route}")
                            break
                        else:
                            # print(f"Non posso inserire il delivery vertex {delivery_vertex} in posizione {delivery_position}")
                            route.remove(delivery_vertex)
                    if delivery_inserted:
                        break
                else:
                    # print(f"Non posso inserire pickup {vertex} in posizione {pickup_position}")
                    route.remove(candidate_vertex)

    for route in routes:
        if route == [source, sink]:
            routes.remove(route)

    # print(f"NEW SOLUTION:")
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
    return routes, arrival_time, route_duration, total_distance

def random_perturbation(routes, arrival_time, route_duration, total_distance):
    """
    Random perturbation
    """
    # Select random vertex
    random_pickup = random.choice(pickup_points)
    random_delivery = random_pickup + num_clients
    print(f"Routes prima {routes}")
    print(f"at {arrival_time}")

    # Remove from current route
    for route in routes:
        print(f"ROUTE DEB {route}")
        if random_pickup in route:
            tabu_route = route
            index = route.index(random_pickup)
            route.remove(random_pickup)
            route.remove(random_delivery)
            del arrival_time[random_pickup]
            del arrival_time[random_delivery]
            arrival_time = update_arrival_times(route, route[index], arrival_time)

    print(f"Routes dopo {routes}")
    print(f"Tabu route: {tabu_route}")


    # Insert in an other route
    for route in routes:
        if route != tabu_route:
            pickup_positions = get_pickup_positions(random_pickup, route, arrival_time)
            if len(pickup_positions) != 0:
                route.insert(random.choice(list(pickup_positions.keys())), random_pickup)
                arrival_time = update_arrival_times(route, random_pickup, arrival_time)
                delivery_positions = get_delivery_positions(random_delivery, route, arrival_time)
                if len(delivery_positions) != 0:
                    selected_delivery = random.choice(list(delivery_positions.keys()))
                    route.insert(selected_delivery, random_delivery)
                    arrival_time = update_arrival_times(route, random_delivery, arrival_time)
                else:
                    print("No delivery positions available")
            else:
                print("No pickup positions available")

    print(f"NEW SOLUTION:")
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
