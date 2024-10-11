import pandas as pd
import math

def calculate_distances(data, set1, set2):
    distance = {}
    for i in set1:
        for j in set2:
            if i != j:
                distance[i, j] = math.sqrt(
                    (data.loc[j, 'latitude'] - data.loc[i, 'latitude']) ** 2
                    + (data.loc[j, 'longitude'] - data.loc[i, 'longitude']) ** 2
                )
    return distance
def read_file(filename):

    data = {}

    with open(filename, 'r') as file:
        # Read the header line
        header_line = file.readline().split()
        num_vehicles = int(header_line[0])
        num_clients = int(header_line[1])
        max_route_duraton = int(header_line[2])
        max_capacity = int(header_line[3])
        max_ride_time_client = int(header_line[4])

        # Read the node data (modified for DataFrames)
        node_data = []  # Store node data as a list of lists for DataFrame creation
        for line in file:
            parts = line.split()
            node_data.append([
                int(parts[0]),
                float(parts[1]),
                float(parts[2]),
                int(parts[3]),
                int(parts[4]),
                int(parts[5]),
                int(parts[6])
            ])

        # Create the DataFrame
        data = pd.DataFrame(node_data, columns=[
            'id', 'latitude', 'longitude', 'service_time', 'demand', 'earliest_time', 'latest_time'
        ])

        print("num vehicles = ", num_vehicles, "with max_capacity", max_capacity)
        print("num clients = ", num_clients)
        print("max route duration = ", max_route_duraton)
        print("max ride time of a client = ", max_ride_time_client)

        source = 0
        sink = 2 * num_clients + 1
        print("Source = ", source, "Sink = ", sink)
        vehicles = list(range(num_vehicles))
        print("vehicles = ", vehicles)

        all_points = list(range(2 * num_clients + 1))
        all_points[0] = source
        all_points.append(sink)
        print("All points = ", all_points)

        points_no_depots = list(all_points)
        points_no_depots.remove(source)
        points_no_depots.remove(sink)
        print("Points no depots = ", points_no_depots)

        pickup_points = list(points_no_depots[:num_clients])
        delivery_points = list(points_no_depots[num_clients:])
        print("Pickup points = ", pickup_points)
        print("Delivery points = ", delivery_points)

        set1 = list(pickup_points + delivery_points)
        set1.append(source)
        set2 = list(pickup_points + delivery_points)
        set2.append(sink)
        print("set1 = ", set1)
        print("set2 = ", set2)

        distance = calculate_distances(data, set1, set2)

        cost = {}
        for vehicle in vehicles:
            for (pickup_point, delivery_point), dist in distance.items():
                cost[pickup_point, delivery_point, vehicle] = distance[pickup_point, delivery_point]

        # print("Distances: ", )
        # res = sum(distance.values()) / len(distance)
        # print("Dist media = ", res)

        service_time = {}
        demand = {}
        latest_time = {}
        earliest_time = {}
        for i in all_points:
            service_time[i] = data.loc[i, 'service_time']
            demand[i] = data.loc[i, 'demand']
            latest_time[i] = data.loc[i, 'latest_time']
            earliest_time[i] = data.loc[i, 'earliest_time']
        print("Service times = ", service_time)
        print("Demand = ", demand)
        print("Latest time = ", latest_time)
        print("Earliest time = ", earliest_time)

    return (num_vehicles, num_clients, max_route_duraton, max_capacity, max_ride_time_client, source, sink,
            vehicles, all_points, points_no_depots, pickup_points, delivery_points, set1, set2,
            distance, cost, service_time, demand, latest_time, earliest_time)


