from construction import (num_clients, max_capacity, max_route_duration,
                          max_ride_time_client, sink, pickup_points, delivery_points,
                          service_time, demand,
                          earliest_time,
                          latest_time, num_vehicles, construction, relocation)
from tests import is_feasible
import time

# TEST SOLUZIONE MODELLO CORDEAU
''' 20 clients 2 vehicles. Feasible solution (not optimal) 
routes = [[0, 7, 9, 4, 2, 1, 24, 27, 29, 22, 21, 13, 16, 3, 18, 20, 15, 36, 38, 35, 40, 33, 23, 41], [0, 17, 19, 12, 11, 14, 34, 37, 39, 32, 31, 5, 10, 8, 6, 25, 30, 28, 26, 41]]
arrival_time = {0: 0.0, 7: 5.879999999999999, 9: 10.338333333300003, 4: 14.714999999999913, 2: 17.453333333299305, 1: 19.631666666599244, 24: 30.0, 27: 31.0, 29: 32.0, 22: 33.0, 21: 34.0, 13: 68.96666666666667, 16: 72.05833333336655, 3: 74.8, 18: 76.24333333330026, 20: 82.45333333330012, 15: 85.0683333333, 36: 90.0, 38: 91.0, 35: 92.0, 40: 93.0, 33: 94.0, 23: 105.0, 41: 120.0, 17: 6.83, 19: 11.03166666669992, 12: 15.133333333333333, 11: 17.35833333339992, 14: 21.51333333339992, 34: 30.0, 37: 31.0, 39: 32.0, 32: 33.0, 31: 35.308333333299984, 5: 44.0, 10: 46.61499999999973, 8: 50.42999999999956, 6: 54.78833333329932, 25: 90.0, 30: 91.0, 28: 92.0, 26: 93.0}
route_duration = {}
for route in routes:
    route_index = routes.index(route)
    route_duration[route_index] = arrival_time[route[len(route) - 2]] + time[route[len(route) - 2], sink]
'''


# start_time = time.time()
# routes, arrival_time, route_duration, total_distance = construction(2)
# end_time = time.time()
# print(f"Execution time: {round(end_time - start_time, 2)} s")
# print(f"Usati {len(routes)} veicoli su {num_vehicles}")
# print(f"Solution is feasible? {is_feasible(routes, pickup_points, delivery_points, route_duration, max_route_duration, demand, max_capacity, sink, arrival_time, earliest_time, latest_time, max_ride_time_client, num_clients, service_time)}")
# eur_sol = [routes, arrival_time, route_duration, total_distance]


def run_constructive():
    start_time = time.time()
    routes, arrival_time, route_duration, total_distance = construction(2)
    end_time = time.time()
    print(f"Execution time: {round(end_time - start_time, 2)} s")
    print(f"Usati {len(routes)} veicoli su {num_vehicles}")
    print(f"Solution is feasible? {is_feasible(routes, pickup_points, delivery_points, route_duration, max_route_duration, demand, max_capacity, sink, arrival_time, earliest_time, latest_time, max_ride_time_client, num_clients, service_time)}")
def multiple_run_constructive(num_runs):
    # Initialize variables to store results
    execution_times = []
    total_distances = []
    num_vehicles_used = []

    for run_num in range(1, num_runs + 1):
        print(f"Run {run_num}:")
        # Measure execution time
        start_time = time.time()
        routes, arrival_time, route_duration, total_distance = construction(2)
        end_time = time.time()

        # Calculate and store execution time
        execution_time = end_time - start_time
        execution_times.append(execution_time)

        # Store total distance and number of vehicles used
        total_distances.append(total_distance)
        num_vehicles_used.append(len(routes))

        # Print results for each run
        print(f"Execution time: {round(execution_time, 2)} s")
        print(f"Used {len(routes)} vehicles out of {num_vehicles}")
        print(f"Solution is feasible? {is_feasible(routes, pickup_points, delivery_points, route_duration, max_route_duration, demand, max_capacity, sink, arrival_time, earliest_time, latest_time, max_ride_time_client, num_clients, service_time)}")

    # Calculate average values
    avg_execution_time = sum(execution_times) / num_runs
    avg_total_distance = sum(total_distances) / num_runs
    avg_num_vehicles = sum(num_vehicles_used) / num_runs

    # Print average results
    print(f"\nAverage execution time: {round(avg_execution_time, 2)} s")
    print(f"Average total distance: {round(avg_total_distance, 2)}")
    print(f"Average number of vehicles used: {round(avg_num_vehicles, 2)}")

def run_grasp(max_iter_grasp, max_iter_local_search):
    """
    :param max_iter_grasp: Maximum number of GRASP algorithm
    :param max_iter_local_search: Maximum number of iterations with no improvements
    """

    import copy

    routes, arrival_time, route_duration, total_distance = construction(2)
    eur_sol = (routes, arrival_time, route_duration, total_distance)
    local_search_sol = copy.deepcopy(eur_sol)
    best_sol = copy.deepcopy(eur_sol)

    for i in range(max_iter_grasp):
        routes, arrival_time, route_duration, total_distance = construction(2)
        iteration_count = 0

        while iteration_count < max_iter_local_search:
            routes, arrival_time, route_duration, total_distance = relocation(routes, arrival_time)
            print(f"Solution is feasible? {is_feasible(routes, pickup_points, delivery_points, route_duration, max_route_duration, demand, max_capacity, sink, arrival_time, earliest_time, latest_time, max_ride_time_client, num_clients, service_time)}")

            local_search_sol = (routes, arrival_time, route_duration, total_distance)

            if local_search_sol[3] < best_sol[3]:
                best_sol = copy.deepcopy(local_search_sol)
                iteration_count = 0
                print(f"Distanza = {best_sol[3]} km, numero veicoli = {len(best_sol[0])}")
                print(f"Iniziale {len(eur_sol[0])} veicoli (MAX = {num_vehicles}), finale {len(best_sol[0])}")
                print(f"Iniziale {eur_sol[3]} km, finale {best_sol[3]} km")
                print(f"Solution is feasible? {is_feasible(routes, pickup_points, delivery_points, route_duration, max_route_duration, demand, max_capacity, sink, arrival_time, earliest_time, latest_time, max_ride_time_client, num_clients, service_time)}")
            else:
                iteration_count += 1

    print(f"\nBEST SOLUTION")
    for route in best_sol[0]:
        print(f"Route {route}")
        print(f"Duration {best_sol[2][best_sol[0].index(route)]}")
        for vertex in route:
            if vertex != sink:
                print(f"       Arrival time vertex {vertex} = {best_sol[1][vertex]}")
    print(f"Routes total durations: {best_sol[2]} (max duration {max_route_duration}")
    print(f"TOTAL SOLUTION COST = {best_sol[3]}")
    print(f"\nCOMPARATIVA")
    print(f"Iniziale {len(eur_sol[0])} veicoli (MAX = {num_vehicles}), finale {len(best_sol[0])}")
    print(f"Iniziale {eur_sol[3]} km, finale {best_sol[3]} km")
    print(f"Solution is feasible? {is_feasible(routes, pickup_points, delivery_points, route_duration, max_route_duration,
                                             demand, max_capacity, sink, arrival_time, earliest_time, latest_time,
                                             max_ride_time_client, num_clients, service_time)}")


# run_constructive()
# multiple_run_constructive(10)
run_grasp(30, 20)