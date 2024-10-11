from construction import (num_clients, max_capacity, max_route_duration,
                          max_ride_time_client, sink, pickup_points, delivery_points,
                          service_time, demand,
                          earliest_time,
                          latest_time, num_vehicles, construction_random_delivery, closest_neighbor,
                          construction_wheighted_random_selection, relocation, relocation_best_insertion,
                          relocation_first_insertion)

from tests import is_feasible, is_feasible_no_print
import time

def run_constructive():
    start_time = time.time()
    routes, arrival_time, route_duration, total_distance = construction_random_delivery()
    end_time = time.time()
    print(f"Execution time: {round(end_time - start_time, 2)} s")
    print(f"Usati {len(routes)} veicoli su {num_vehicles}")
    print(f"Solution is feasible? {is_feasible(routes, pickup_points, delivery_points, route_duration, max_route_duration,
                                             demand, max_capacity, sink, arrival_time, earliest_time, latest_time,
                                             max_ride_time_client, num_clients, service_time)}")
def multiple_run_constructive(num_runs):
    # Initialize variables to store results
    execution_times = []
    total_distances = []
    num_vehicles_used = []

    for run_num in range(1, num_runs + 1):
        print(f"Run {run_num}:")
        # Measure execution time
        start_time = time.time()
        routes, arrival_time, route_duration, total_distance = closest_neighbor()
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
        print(f"Solution is feasible? {is_feasible(routes, pickup_points, delivery_points, route_duration, max_route_duration,
                                                 demand, max_capacity, sink, arrival_time, earliest_time, latest_time,
                                                 max_ride_time_client, num_clients, service_time)}")

    # Calculate average values
    avg_execution_time = sum(execution_times) / num_runs
    avg_total_distance = sum(total_distances) / num_runs
    avg_num_vehicles = sum(num_vehicles_used) / num_runs

    # Print average results
    print(f"\nAverage execution time: {round(avg_execution_time, 2)} s")
    print(f"Average total distance: {round(avg_total_distance, 2)}")
    print(f"Average number of vehicles used: {round(avg_num_vehicles, 2)}")

def run_multi_start_relocation(num_starts, max_iter_no_improvements):
    """
    :param num_starts: Maximum number of algorithm iterations
    :param max_iter_no_improvements: Maximum number of loca search iterations with no improvements
    """

    import copy
    print(f"\nRunning Multi Start Relocation with:")
    print(f"- Maximum number of algorithm iterations: {num_starts}")
    print(f"- Maximum number of Relocation iteretions with no improvements: {max_iter_no_improvements}")

    start_time = time.time()
    routes, arrival_time, route_duration, total_distance = construction_random_delivery()
    eur_sol = copy.deepcopy((routes, arrival_time, route_duration, total_distance))
    relocation_sol = copy.deepcopy(eur_sol)
    best_sol = copy.deepcopy(eur_sol)

    for i in range(num_starts):
        routes, arrival_time, route_duration, total_distance = construction_random_delivery()
        iteration_count = 0

        while iteration_count < max_iter_no_improvements:
            # routes, arrival_time, route_duration, total_distance = relocation_first_insertion(routes, arrival_time)
            routes, arrival_time, route_duration, total_distance = relocation_best_insertion(routes, arrival_time, route_duration, total_distance)
            # print(f"Solution is feasible? {is_feasible(routes, demand, max_capacity, sink, arrival_time, earliest_time, latest_time, pickup_points, delivery_points)}")
            relocation_sol = (routes, arrival_time, route_duration, total_distance)
            feasible_flag = is_feasible_no_print(routes, pickup_points, delivery_points, route_duration, max_route_duration,
                                             demand, max_capacity, sink, arrival_time, earliest_time, latest_time,
                                             max_ride_time_client, num_clients, service_time)


            if relocation_sol[3] < best_sol[3] and feasible_flag:
                best_sol = copy.deepcopy(relocation_sol)
                iteration_count = 0
                print(f"New best solution found: distance = {best_sol[3]} km, number of vehicles = {len(best_sol[0])}")
                # print(f"Iniziale {len(eur_sol[0])} veicoli (MAX = {num_vehicles}), finale {len(best_sol[0])}")
                # print(f"Iniziale {eur_sol[3]} km, finale {best_sol[3]} km")
                # print(
                #     f"Solution is feasible? {is_feasible(routes, pickup_points, delivery_points, route_duration, max_route_duration,
                #                                          demand, max_capacity, sink, arrival_time, earliest_time, latest_time,
                #                                          max_ride_time_client, num_clients, service_time)}")
            else:
                iteration_count += 1

    print(f"\nBEST SOLUTION")
    end_time = time.time()
    for route in best_sol[0]:
        print(f"Route {route}")
        print(f"Duration {best_sol[2][best_sol[0].index(route)]}")
        for vertex in route:
            if vertex != sink:
                print(f"       Arrival time vertex {vertex} = {best_sol[1][vertex]}")
    print(f"Routes total durations: {best_sol[2]} (max duration {max_route_duration}")
    print(f"TOTAL SOLUTION COST = {best_sol[3]}")
    print(f"\nCOMPARATIVA")
    print(f"Multi Start Relocation execution time: {round(end_time - start_time, 2)} s")
    print(f"Iniziale {len(eur_sol[0])} veicoli (MAX = {num_vehicles}), finale {len(best_sol[0])}")
    print(f"Iniziale {eur_sol[3]} km, finale {best_sol[3]} km")
    print(f"Solution is feasible? {is_feasible(best_sol[0], pickup_points, delivery_points, best_sol[2], max_route_duration,
                                             demand, max_capacity, sink, best_sol[1], earliest_time, latest_time,
                                             max_ride_time_client, num_clients, service_time)}")


# run_constructive()
# multiple_run_constructive(10)
run_multi_start_relocation(5, 200)
