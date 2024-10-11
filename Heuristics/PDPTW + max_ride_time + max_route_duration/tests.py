def check_route_capacity(route, demand, max_capacity):
    capacity = 0
    for vertex in route:
        capacity += demand[vertex]
        if capacity > max_capacity:
            return False
    return True
def check_time_windows(route, routes, route_duration, sink, arrival_time, earliest_time, latest_time):
    for vertex in route:
        if vertex != sink:
            # print(f"vertice {vertex} tw[{earliest_time[vertex], latest_time[vertex]}] , arrival time {arrival_time[vertex]}")
            if arrival_time[vertex] < earliest_time[vertex]:
                # print(f"Arrival time vertex {vertex} is {arrival_time[vertex]} but earliest time is {earliest_time[vertex]}")
                return False
            if arrival_time[vertex] > latest_time[vertex]:
                # print(f"Arrival time vertex {vertex} is {arrival_time[vertex]} but latest time is {latest_time[vertex]}")
                return False
    return True
def ride_time_client(client, route, arrival_time_dictionary, num_clients, service_time):
    corresponding_delivery_vertex = client + num_clients
    t1 = arrival_time_dictionary[corresponding_delivery_vertex]
    t2 = arrival_time_dictionary[client] + service_time[client]
    return t1-t2
def check_ride_times(route, arrival_time_dictionary, pickup_points, max_ride_time_client, num_clients, service_time):
    for client in route:
        if client in pickup_points:
            corresponding_delivery_vertex = client + num_clients
            t1 = arrival_time_dictionary[corresponding_delivery_vertex]
            t2 = arrival_time_dictionary[client] + service_time[client]
            ride_time = t1 - t2
            if ride_time > max_ride_time_client:
                print(f"ride time client {client} = {ride_time} min, but MAX = {max_ride_time_client}")
                return False
    return True
def check_route_duration(route, routes, route_duration, max_route_duration):
    route_index = routes.index(route)
    duration = route_duration[route_index]
    if duration <= max_route_duration:
        return True
    else:
        return False
def check_used_points(pickup_points, delivery_points, routes):
    import copy
    pickup_copy = copy.deepcopy(pickup_points)
    delivery_copy = copy.deepcopy(delivery_points)
    for route in routes:
        for vertex in route:
            if vertex in pickup_points:
                pickup_copy.remove(vertex)
            if vertex in delivery_copy:
                delivery_copy.remove(vertex)
    if pickup_copy == []:
        print(f"All pickup used")
    else:
        print("ERROR! Not all pickup points used")
    if delivery_copy == []:
        print(f"All delivery used")
    else:
        print("ERROR! Not all delivery points used")
def is_feasible(routes, pickup_points, delivery_points, route_duration, max_route_duration, demand, max_capacity, sink, arrival_time, earliest_time, latest_time, max_ride_time_client, num_clients, service_time):
    check_used_points(pickup_points, delivery_points, routes)
    for route in routes:
        if not check_route_capacity(route, demand, max_capacity):
            print("Too big route capacity")
            return False
        if not check_time_windows(route, routes, route_duration, sink, arrival_time, earliest_time, latest_time):
            print("Time windows constraint not met")
            return False
        if not check_route_duration(route, routes, route_duration, max_route_duration):
            print("Too big route duration")
            return False
        if not check_ride_times(route, arrival_time, pickup_points, max_ride_time_client, num_clients, service_time):
            print("Too big ride times")
            return False
    return True

def is_feasible_no_print(routes, pickup_points, delivery_points, route_duration, max_route_duration, demand, max_capacity, sink, arrival_time, earliest_time, latest_time, max_ride_time_client, num_clients, service_time):
    # check_used_points(pickup_points, delivery_points, routes)
    for route in routes:
        if not check_route_capacity(route, demand, max_capacity):
            # print("Too big route capacity")
            return False
        if not check_time_windows(route, routes, route_duration, sink, arrival_time, earliest_time, latest_time):
            # print("Time windows constraint not met")
            return False
        if not check_route_duration(route, routes, route_duration, max_route_duration):
            # print("Too big route duration")
            return False
        if not check_ride_times(route, arrival_time, pickup_points, max_ride_time_client, num_clients, service_time):
            # print("Too big ride times")
            return False
    return True

