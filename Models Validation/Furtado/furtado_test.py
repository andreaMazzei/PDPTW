import gurobipy as gp
from gurobipy import GRB
import read_data
import cordeau_read_data

filename = "../../Dataset/Furtado Validation/DD10.dat"

(num_clients, max_capacity, demand, earliest_time, latest_time, cost, times, source,
            sink, all_points, points_no_depots, pickup_points, delivery_points, set1, set2,
            distance, service_time, penalty) = read_data.read_file(filename)

print("IL NUMERO DI VEICOLI NON È IMPOSTO MA SCELTO DAL MODELLO!")
print("Vehicle capacity", max_capacity)
print("num clients = ", num_clients)
print("PDPTW Compact formulation")
model = gp.Model("Furtado Validation")
model.reset()


# x[i, j] binary variable. = 1 if vehicle k travels from node i to node j
x = model.addVars(times, vtype=GRB.BINARY, name="x")
# Q[i] = vehicle load when after visiting vertex i
Q = model.addVars(all_points, lb = 0, vtype=GRB.CONTINUOUS, name="Q")
# B[i] = time of beginning service at vertex i
B = model.addVars(all_points, lb = 0, vtype=GRB.CONTINUOUS, name="B")
# Continuous decision variable that is equal to the index of the first node in the route that visits node i
v = model.addVars(points_no_depots, vtype=GRB.CONTINUOUS, name="v")

# Objective function
model.setObjective(gp.quicksum(x[source, j]*penalty for j in set2) + x.prod(cost), GRB.MINIMIZE)
# model.setObjective(x.prod(cost), GRB.MINIMIZE)


# Constraints
#in un client entra un solo arco
model.addConstrs(gp.quicksum(x[i, j] for i in all_points if i != j and i != sink) == 1 for j in points_no_depots)
# da un client esce un solo arco
model.addConstrs(gp.quicksum(x[i, j] for j in all_points if i != j and j != source) == 1 for i in points_no_depots)
model.addConstrs((x[i, j] == 1) >> (B[j] >= B[i] + times[i, j]) for i in all_points for j in all_points if i != j and i != sink and j != source)
model.addConstrs((x[i, j] == 1) >> (Q[j] >= Q[i] + demand[j]) for i in all_points for j in all_points if i != j and i != sink and j != source)
model.addConstrs(B[i] >= earliest_time[i] for i in all_points)
model.addConstrs(B[i] <= latest_time[i] for i in all_points)
model.addConstrs(Q[i] >= max(0, demand[i]) for i in all_points)
model.addConstrs(Q[i] <= min(max_capacity, max_capacity + demand[i]) for i in all_points)
model.addConstrs(B[num_clients + i] >= B[i] + times[i, num_clients + i] for i in pickup_points)
model.addConstrs(v[num_clients + i] == v[i] for i in pickup_points)
model.addConstrs(v[j] >= j * x[source, j] for j in points_no_depots)
model.addConstrs(v[j] <= j * x[source, j] - num_clients * (x[source, j] - 1) for j in points_no_depots)
model.addConstrs(v[j] >= v[i] + num_clients * (x[i, j] - 1) for i in points_no_depots for j in points_no_depots if i != j)
model.addConstrs(v[j] <= v[i] + num_clients * (1 - x[i, j]) for i in points_no_depots for j in points_no_depots if i != j)

model.setParam('InfUnbdInfo', 1)

model.optimize()

# If the model is infeasible or unbounded, this will print more detailed information about the cause
if model.status in [GRB.INFEASIBLE, GRB.INF_OR_UNBD]:
    model.computeIIS()
    model.write("model.ilp")


sol = {k for k, v in x.items() if v.X > 0.01}
print("Total cost = ", model.objval)
print(sol)

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
print("Costo della soluzione = ", model.objval)
print("Numero veicoli utilizzati = ", len(routes))

