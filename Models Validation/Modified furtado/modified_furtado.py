import gurobipy as gp
from gurobipy import GRB
import read_data

filename = "../../Dataset/Cordeau Validation/a4-16.txt"

(num_vehicles, num_clients, max_route_duration, capacity, max_ride_time_client, source, sink,
 vehicles, all_points, points_no_depots, pickup_points, delivery_points,
 set1, set2, distance, cost, service_time, demand, latest_time, earliest_time) = read_data.read_file(filename)


penalty = 100

print("IL NUMERO DI VEICOLI NON È IMPOSTO MA SCELTO DAL MODELLO!")
print("Vehicle capacity", capacity)
print("num clients = ", num_clients)
print("PDPTW Compact formulation")
model = gp.Model("Multi vehicle DARP heuristics")
model.reset()
maxTime_minutes = 30 #minutes
timelimit = maxTime_minutes * 60
model.Params.timelimit = timelimit

# x[i, j] binary variable. = 1 if vehicle k travels from node i to node j
x = model.addVars(distance, vtype=GRB.BINARY, name="x")
# Q[i] = vehicle load when after visiting vertex i
Q = model.addVars(all_points, lb = 0, vtype=GRB.CONTINUOUS, name="Q")
# B[i] = time of beginning service at vertex i
B = model.addVars(all_points, lb = 0, vtype=GRB.CONTINUOUS, name="B")
# Continuous decision variable that is equal to the index of the first node in the route that visits node i
v = model.addVars(points_no_depots, vtype=GRB.CONTINUOUS, name="v")

# Objective function
# model.setObjective(gp.quicksum(x[source, j]*penalty for j in set2) + x.prod(distance), GRB.MINIMIZE)
model.setObjective(x.prod(distance), GRB.MINIMIZE)

# Constraints
#in un client entra un solo arco
model.addConstrs(gp.quicksum(x[i, j] for i in all_points if i != j and i != sink) == 1 for j in points_no_depots)
# da un client esce un solo arco
model.addConstrs(gp.quicksum(x[i, j] for j in all_points if i != j and j != source) == 1 for i in points_no_depots)
model.addConstrs((x[i, j] == 1) >> (B[j] >= B[i] + service_time[i] + distance[i, j]) for i in all_points for j in all_points if i != j and i != sink and j != source)
model.addConstrs((x[i, j] == 1) >> (Q[j] >= Q[i] + demand[j]) for i in all_points for j in all_points if i != j and i != sink and j != source)
model.addConstrs(B[i] >= earliest_time[i] for i in all_points)
model.addConstrs(B[i] <= latest_time[i] for i in all_points)
model.addConstrs(Q[i] >= max(0, demand[i]) for i in all_points)
model.addConstrs(Q[i] <= min(capacity, capacity + demand[i]) for i in all_points)
model.addConstrs(B[num_clients + i] >= B[i] + service_time[i] + distance[i, num_clients + i] for i in pickup_points)
model.addConstrs(v[num_clients + i] == v[i] for i in pickup_points)
model.addConstrs(v[j] >= j * x[source, j] for j in points_no_depots)
model.addConstrs(v[j] <= j * x[source, j] - num_clients * (x[source, j] - 1) for j in points_no_depots)
model.addConstrs(v[j] >= v[i] + num_clients * (x[i, j] - 1) for i in points_no_depots for j in points_no_depots if i != j)
model.addConstrs(v[j] <= v[i] + num_clients * (1 - x[i, j]) for i in points_no_depots for j in points_no_depots if i != j)

# VINCOLI EXTRA NON NEL MODELLO ORIGINALE
# Max ride time
model.addConstrs(B[num_clients + i] - (B[i] + service_time[i])  <= max_ride_time_client for i in pickup_points)
# Max route duration
model.addQConstr(B[sink] <= max_route_duration)
# Max number of vehicles
model.addConstr(gp.quicksum(x[source, j] for j in points_no_depots) <= num_vehicles)



model.setParam('InfUnbdInfo', 1)
# model.setParam('LogFile', filename+'_result.txt')
model.optimize()

if model.status in [GRB.INFEASIBLE, GRB.INF_OR_UNBD]:
    model.computeIIS()
    model.write("model.ilp")

sol = {k for k, v in x.items() if v.X > 0.01}
sol_B = {k: v.X for k, v in B.items()}

print("Total cost (distance) = ", round(model.objval, 3), "km")
def route(solution):
    routes = []
    for arc in solution:
        if arc[0] == source:
            route = []
            route.append(arc[0])
            route.append(arc[1])
            routes.append(route)
    for route in routes:
      while route[-1] != sink:
          for arc in solution:
              if arc[0] == route[-1]:
                  route.append(arc[1])
    return routes

routes = route(sol)


print("Routes: ", routes)
print("Numero veicoli utilizzati = ", len(routes))

print(f"\nArrival times:")
for route in routes:
    print(f"Route: {route}")
    for vertex in route:
        if vertex != sink:
            print(f"      Arrival time at node {vertex} = {sol_B[vertex]}")
        else:
            last_vertex = route[-2]
            print(f"      Arrival time at node {sink} = {sol_B[last_vertex] + service_time[last_vertex] + time[last_vertex, sink]}")


print(f"\nRide times:")
for route in routes:
    print(f"Route: {route}")
    for vertex in route:
        if vertex in pickup_points:
            print(f"      Ride time client {vertex} = {sol_B[num_clients + vertex] - (sol_B[vertex] + service_time[vertex])}")

