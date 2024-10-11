import gurobipy as gp
from gurobipy import GRB
import read_data

filename = "../../Dataset/Cordeau Validation/a2-20.txt"

(num_vehicles, num_clients, max_route_duration, capacity, max_ride_time_client, source, sink,
 vehicles, all_points, points_no_depots, pickup_points, delivery_points,
 set1, set2, distance, cost, service_time, demand, latest_time, earliest_time) = read_data.read_file(filename)

print("Multi vehicle DARP heuristics")
print("Minimizing total route distance (cost(i,j,k) = distance(i,j,k))")
print("Distanza media = ", sum(distance.values()) / len(distance))
model = gp.Model("Multi vehicle DARP heuristics")
model.reset()
maxTime_minutes = 30 #minutes
timelimit = maxTime_minutes * 60
model.Params.timelimit = timelimit

# x[i, j, k] binary variable. = 1 if vehicle k travels from node i to node j
x = model.addVars(cost, vtype=GRB.BINARY, name="x")
# Q[i,k] = load of vehicle k when leaving vertex i
# B[i,k] = beginning of service of vehicle k at vertex i (arrival time)
# L[i, k] = ride time of user i with vehicle k
Q = {}
B = {}
L = {}

# tmp = {}
for i in all_points:
    for k in vehicles:
        # tmp[i,k] = 1
        Q[(i, k)] = model.addVar(vtype=GRB.CONTINUOUS, name="Q[%d,%d]" % (i,k))
        B[(i, k)] = model.addVar(vtype=GRB.CONTINUOUS, name="B[%d,%d]" % (i,k))
for i in pickup_points:
    for k in vehicles:
        L[(i, k)] = model.addVar(vtype=GRB.CONTINUOUS, name="L[%d,%d]" % (i,k))

# Objective function
model.setObjective(x.prod(cost), GRB.MINIMIZE)

# Cordeau Validation Models Validation Model
model.addConstrs(gp.quicksum(x[i, j, k] for j in set2 for k in vehicles if i != j) == 1 for i in pickup_points)
model.addConstrs(gp.quicksum(x[i, j, k] for j in set2 if i != j) - gp.quicksum(x[num_clients + i, j, k] for j in set2 if num_clients + i != j) == 0 for i in pickup_points for k in vehicles)
model.addConstrs(gp.quicksum(x[source, j, k] for j in set2) == 1 for k in vehicles)
model.addConstrs(gp.quicksum(x[j, i, k] for j in set1 if i != j) - gp.quicksum(x[i, j, k] for j in set2 if i != j) == 0 for i in points_no_depots for k in vehicles)
model.addConstrs(gp.quicksum(x[i, sink, k] for i in set1) == 1 for k in vehicles)
model.addConstrs((x[i, j, k] == 1) >> (B[j, k] >= (B[i, k] + service_time[i] + distance[i, j])) for i in set1 for j in set2 for k in vehicles if i != j)
model.addConstrs((x[i, j, k] == 1) >> (Q[j, k] >= (Q[i, k] + demand[j])) for i in set1 for j in set2 for k in vehicles if i != j)
model.addConstrs(L[i, k] == B[num_clients + i, k] - (B[i, k] + service_time[i]) for i in pickup_points for k in vehicles)
model.addConstrs(B[sink, k] - B[source, k] <= max_route_duration for k in vehicles)
model.addConstrs(B[i, k] <= latest_time[i] for i in all_points for k in vehicles)
model.addConstrs(B[i, k] >= earliest_time[i] for i in all_points for k in vehicles)
model.addConstrs(L[i, k] >= distance[i, num_clients + i] for i in pickup_points for k in vehicles)
model.addConstrs(L[i, k] <= max_ride_time_client for i in pickup_points for k in vehicles)
model.addConstrs(Q[i, k] >= max(0, demand[i]) for i in all_points for k in vehicles)
model.addConstrs(Q[i, k] <= min(capacity, capacity + demand[i]) for i in all_points for k in vehicles)

model.setParam('InfUnbdInfo', 1)
model.setParam('LogFile', filename+'_result.txt')
model.optimize()

if model.status in [GRB.INFEASIBLE, GRB.INF_OR_UNBD]:
    model.computeIIS()
    model.write("model.ilp")

def print_sol_x(sol):
    k_lists = {}
    route = {}
    for (i, j, k), value in sol.items():
        if k not in k_lists:
            k_lists[k] = []
        k_lists[k].append((i, j))
    for k, values in k_lists.items():
        print(f"Vehicle {k}: {values}")
def print_sol_Q(sol):
    k_lists = {}
    for (i, k), v in sol.items():
        if k not in k_lists:
            k_lists[k] = []
        k_lists[k].append((i, v))
    for k, values in k_lists.items():
        print(f"   Load of vehicle = {k}")
        for i, v in values:
            print(f"      Visited Node {i}: Load = {v}")
        print()  # Add an empty line between vehicles
def print_sol_B(sol):
    k_lists = {}
    print()
    for (i, k), v in sol.items():
        if k not in k_lists:
            k_lists[k] = []
        k_lists[k].append((i, v))
    for k, values in k_lists.items():
        print(f"   Vehicle = {k}")
        for i, v in values:
            print(f"      Beginning service time at node {i} = {v}")
        print()
def print_sol_L(sol):
    k_lists = {}
    print()
    for (i, k), v in sol.items():
        if k not in k_lists:
            k_lists[k] = []
        k_lists[k].append((i, v))
    for k, values in k_lists.items():
        print(f"   Vehicle = {k}")
        for i, v in values:
            print(f"      Ride time of user {i} = {v}")
        print()
def routes(sol_x):
    routes_by_vehicle = {}
    sol = []
    for route, _ in sol_x.items():
        vehicle_id = route[2]
        if vehicle_id not in routes_by_vehicle:
            routes_by_vehicle[vehicle_id] = []
        routes_by_vehicle[vehicle_id].append(route)

    for vehicle_id, routes in routes_by_vehicle.items():
        path = [0]
        while True:
            current_node = path[-1]
            for route in routes:
                if route[0] == current_node:
                    path.append(route[1])
                    routes.remove(route)
                    break
            else:
                break

        print(f"Vehicle {vehicle_id}: {path}")
        sol.append(path)
    return sol

sol_x = {k: v.X for k, v in x.items() if v.X > 0.01}
sol_Q = {k: v.X for k, v in Q.items()}
sol_B = {k: v.X for k, v in B.items()}
sol_L = {k: v.X for k, v in L.items()}

print("Total distance = ", round(model.objval, 3))
print("Routes:")
routes = routes(sol_x)

# Arrival times
print(f"\nArrival times:")
for route_index in range(len(routes)):
    print(f"    Vehicle {route_index}:")
    for vertex in routes[route_index]:
        print(f"      Arrival time at node {vertex} = {sol_B[vertex, route_index]}")

# Ride times
print(f"\nRide times:")
for route_index in range(len(routes)):
    print(f"    Vehicle {route_index}:")
    for vertex in routes[route_index]:
        if vertex in pickup_points:
            print(f"      Ride time client {vertex} = {sol_L[vertex, route_index]}")

