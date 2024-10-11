import math
import pandas as pd
from tabulate import tabulate


def read_file(filename):
    data = {}
    with open(filename, 'r') as file:
        for line in file:
            key, value_str = line.strip().split(':')
            value_str = value_str.strip()

            # Determine variable type and convert values
            if key in ['Cap', 'n', 'xc', 'yc', 'p']:
                try:
                    value = int(value_str)
                except ValueError:
                    print(f"Warning: Invalid value '{value_str}' for key '{key}'. Skipping...")
                    continue
            elif key in ['q', 'd', 'e', 'l', 'coorx', 'coory']:
                value = []
                for x in value_str.split():
                    try:
                        value.append(int(x.strip('[]')))  # Remove brackets
                    except ValueError:
                        print(f"Warning: Invalid element '{x}' in list for key '{key}'. Skipping...")
            else:
                # Handle unexpected keys if needed
                value = value_str

            data[key] = value

    # Unpack dictionary into variables
    max_capacity = data.get('Cap', None)  # Use .get() with default value None for safety
    num_clients = data.get('n', None)
    demand = data.get('q', [])
    service_time = data.get('d', [])
    earliest_time = data.get('e', [])
    latest_time = data.get('l', [])
    coorx = data.get('coorx', [])
    coory = data.get('coory', [])
    xc = data.get('xc', None)
    yc = data.get('yc', None)
    penalty = data.get('p', None)

    # con coorx coory xc e yc
    demand.insert(0, 0)
    demand.insert(len(demand), 0)

    service_time.insert(0, 0)
    service_time.insert(len(service_time), 0)

    earliest_time.insert(0, 0)
    earliest_time.insert(len(earliest_time), 0)

    latest_time.insert(0, 1000000)
    latest_time.insert(len(latest_time), 1000000)

    coorx.insert(0, xc)
    coorx.insert(len(coorx), xc)

    coory.insert(0, yc)
    coory.insert(len(coory), yc)

    source = 0
    sink = 2 * num_clients + 1
    print("Source = ", source, "Sink = ", sink)

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



    # Calculate distances
    distance = {}
    for i in set1:
        for j in set2:
            if i != j:
                distance[i, j] = math.sqrt((coorx[j] - coorx[i]) ** 2 + (coory[j] - coory[i]) ** 2)

    cost = distance
    times = {}
    for key in distance:
        times[key] = distance[key] + service_time[key[1]]

    print("Cost = ", cost)
    print("Times = ", times)

    return (num_clients, max_capacity, demand, earliest_time, latest_time, cost, times, source,
            sink, all_points, points_no_depots, pickup_points, delivery_points, set1, set2,
            distance, service_time, penalty)




