
def check_route_capacity(route, demand, max_capacity):
    capacity = 0
    for vertex in route:
        capacity += demand[vertex]
        if capacity > max_capacity:
            return False
    return True
def check_time_windows(route, sink, arrival_time, earliest_time, latest_time):
    for vertex in route:
        if vertex != sink:
            if arrival_time[vertex] < earliest_time[vertex]:
                return False
            if arrival_time[vertex] > latest_time[vertex]:
                return False
    return True
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
        print(pickup_copy)
    if delivery_copy == []:
        print(f"All delivery used")
    else:
        print(delivery_copy)
def is_feasible(routes, demand, max_capacity, sink, arrival_time, earliest_time, latest_time, pickup_points, delivery_points):
    check_used_points(pickup_points, delivery_points, routes)
    for route in routes:
        if not check_route_capacity(route, demand, max_capacity):
            print("Too big route capacity")
            return False
        if not check_time_windows(route, sink, arrival_time, earliest_time, latest_time):
            print("Time windows constraint not met")
            return False
    return True

def is_feasible_no_print(routes, demand, max_capacity, sink, arrival_time, earliest_time, latest_time, pickup_points, delivery_points):
    # check_used_points(pickup_points, delivery_points, routes)
    for route in routes:
        if not check_route_capacity(route, demand, max_capacity):
            # print("Too big route capacity")
            return False
        if not check_time_windows(route, sink, arrival_time, earliest_time, latest_time):
            # print("Time windows constraint not met")
            return False
    return True
