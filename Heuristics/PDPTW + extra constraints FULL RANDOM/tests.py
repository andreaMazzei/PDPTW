def check_route_duration(route, routes, route_duration, max_route_duration):
    route_index = routes.index(route)
    duration = route_duration[route_index]
    # duration = arrival_time[route[len(route) - 2]] + time[route[len(route) - 2], sink]
    if duration <= max_route_duration:
        return True
    else:
        return False
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
        else:
            route_index = routes.index(route)
            if route_duration[route_index] < earliest_time[sink]:
                return False
            if route_duration[route_index] > latest_time[sink]:
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
            ride_time = ride_time_client(client, route, arrival_time_dictionary, num_clients, service_time)
            if ride_time > max_ride_time_client:
                print(f"ride time client {client} = {ride_time} min, but MAX = {max_ride_time_client}")
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
def is_feasible(routes, pickup_points, delivery_points, route_duration, max_route_duration, demand, max_capacity, sink, arrival_time, earliest_time, latest_time, max_ride_time_client, num_clients, service_time):
    check_used_points(pickup_points, delivery_points, routes)
    for route in routes:
        if not check_route_duration(route, routes, route_duration, max_route_duration):
            print("Too big route duration")
            return False
        if not check_route_capacity(route, demand, max_capacity):
            print("Too big route capacity")
            return False
        if not check_time_windows(route, routes, route_duration, sink, arrival_time, earliest_time, latest_time):
            print("Time windows not respected")
            return False
        if not check_ride_times(route, arrival_time, pickup_points, max_ride_time_client, num_clients, service_time):
            # print("Too big ride times")
            return False
    return True



''' EXTRA
def change_route(pickup_vertex, original_route_numeber):
    arrival_time_copy = copy.deepcopy(arrival_time)
    for route_number in range(len(routes)):
        if route_number != original_route_numeber:
            selected_route = routes[route_number]
            pickup_position = best_pickup_position(pickup_vertex, selected_route)
            if pickup_position is not False:
                selected_route.insert(pickup_position, pickup_vertex)
                update_arrival_times(selected_route, pickup_position, arrival_time_copy)
                delivery_vertex = pickup_vertex + num_clients
                delivery_position = best_delivery_position(delivery_vertex, selected_route, candidates)
                if delivery_position is not False:
                    selected_route.insert(delivery_position, delivery_vertex)
                    update_arrival_times(selected_route, delivery_position, arrival_time)
                    print(f"Vertici {pickup_vertex} e {delivery_vertex} spostati nella route {route_number}")
                    break


for route in routes:
    candidates = []
    for client in route:Even 
        if client in pickup_points:
            ride_time = ride_time_client(client, route, arrival_time)
            if ride_time > max_ride_time_client:
                print(f"     ride time client {client} = {ride_time} min, but MAX = {max_ride_time_client}")
                route.remove(client)
                corresponding_delivery_vertex = client + num_clients
                route.remove(corresponding_delivery_vertex)
                candidates.append(client)
    print("candidates = ", candidates)

    arrival_time_copy = copy.deepcopy(arrival_time)

    # If try move the couple of vetexes intra route
    for pickup_vertex in candidates:
        print(f"Selezionato candidato {pickup_vertex}")
        for pickup_position in range(1, len(route)):
            route.insert(pickup_position, pickup_vertex)
            print(f"Vertice pickup {pickup_vertex} Inserito temporaneamente nella posizione {pickup_position}")
            # Update all arrivals time after insertion
            arrival_time_copy = update_arrival_times(route, pickup_position, arrival_time_copy)
            # check for each vertex that TW is respected
            if (check_route_capacity(route) and feasible_insertion(pickup_vertex, route, pickup_position, arrival_time_copy)):
                delivery_vertex = pickup_vertex + num_clients
                for delivery_position in range(pickup_position + 1, len(route)):
                    route.insert(delivery_position, delivery_vertex)
                    # Update all arrivals time after insertion
                    arrival_time_copy = update_arrival_times(route, delivery_position, arrival_time_copy)
                    # check for each vertex that TW is respected
                    ride_time = (arrival_time_copy[delivery_vertex] - (arrival_time_copy[pickup_vertex] + service_time[pickup_vertex]))
                    if (check_route_capacity(route) and feasible_insertion(delivery_vertex, route, delivery_position,arrival_time_copy)
                        and check_ride_times(route, arrival_time_copy)):
                        print(f"    INSERIRITO DELIVERY VERTEX {delivery_vertex} nella posizione {delivery_position} -> STOP")
                        print(f"ROUTE: {route}")
                        break
                    else:
                        route.remove(delivery_vertex)
                        print(f"NON POSSO INSERIRE DELIVERY VERTEX {delivery_vertex} nella posizione {delivery_position}, ne provo un'altra")
                        print(f"ROUTE: {route}")

                if delivery_vertex in route:
                    arrival_time = arrival_time_copy
                    # I don't try other pickup positions
                    break
                else:
                    route.remove(pickup_vertex)
                    print(
                        f"NON POSSO INSERIRE PICKUP VERTEX {pickup_vertex} nella posizione {pickup_position}, ne provo un'altra")
                    print(f"ROUTE: {route}")


            else:
                route.remove(pickup_vertex)
                print(f"NON POSSO INSERIRE PICKUP VERTEX {pickup_vertex} nella posizione {pickup_position}, ne provo un'altra")


        # If I can't move the couple of vetexes intra route, I move it in an other route
        if pickup_vertex not in route:
            print(f"Sposto il vertice pickup {pickup_vertex} in un'altra route")
            original_route_numeber = routes.index(route)
            change_route(pickup_vertex, original_route_numeber)


print(routes)
print(f"Solution is feasible (Not checking clients ride times)? {is_feasible(routes)}")
print(f"Solution is feasible (Checking clients ride times)? {is_feasible_v2(routes)}")

'''

