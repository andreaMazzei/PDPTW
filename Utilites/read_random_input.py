import pandas as pd
import haversine as hs
from Utilites.show_map import map_plot

def center_of_gravity(filenames):

  # Combine latitude and longitude data from all files
  combined_latitudes = pd.Series([])
  combined_longitudes = pd.Series([])

  for filename in filenames:
      data = pd.read_csv(filename)
      combined_latitudes = pd.concat([combined_latitudes, data['latitude']])
      combined_longitudes = pd.concat([combined_longitudes, data['longitude']])

  # Calculate the center of gravity
  latitude_cg = combined_latitudes.mean()
  longitude_cg = combined_longitudes.mean()

  # Create DataFrame
  ids = ["Source", "Sink"]
  df = pd.DataFrame({'id': ids, 'latitude': latitude_cg, 'longitude': longitude_cg})
  df.to_csv('Dataset/depots.csv', index=False)

  return df

# Read pickup_points and delivery_points csv file
directory_name = "Dataset/10 clients - 4 vehicles/"

pickup_points_filename = f"{directory_name}pickup_points.csv"
delivery_points_filename = f"{directory_name}delivery_points.csv"

pickup_points_df = pd.read_csv(pickup_points_filename)
delivery_points_df = pd.read_csv(delivery_points_filename)

num_clients = len(pickup_points_df.index)

# Imposing starting depot position = ending depot position = center of gravity of all points
filenames = [pickup_points_filename, delivery_points_filename]
depots_df = center_of_gravity(filenames)

# Read vehicles csv file
vehicles_df = pd.read_csv(directory_name + "/vehicles.csv")

# List of ids of pickup points, delivery points, depots and vehicles
pickup_points = pickup_points_df['id'].tolist()
delivery_points = delivery_points_df['id'].tolist()
depots = depots_df['id'].tolist()
vehicles = vehicles_df['id'].tolist()

# Create a dictionary of demands of points
# Pickup points --> +1, Delivery points --> -1, Depots --> 0
demand = {}
for point in pickup_points:
    demand[point] = 1
for point in delivery_points:
    demand[point] = -1
for point in depots:
    demand[point] = 0

points_no_depots = list(pickup_points + delivery_points)

# Create a dictionary of sevice times of all nodes
service_time = {}
service_time[depots[0]] = 0
service_time[depots[1]] = 0
for point in points_no_depots:
    service_time[point] = 1

set1 = list(pickup_points + delivery_points)
set1.append(depots[0])
set2 = list(pickup_points + delivery_points)
set2.append(depots[1])
all_points_df = pd.concat([pickup_points_df, delivery_points_df, depots_df])
all_points = all_points_df['id'].tolist()

# Create a dictionary of distances (in Km) between points
distance = {}
for point1 in set1:
    for point2 in set2:
        if point1 != point2:
            pickup_df = all_points_df.loc[all_points_df['id'] == point1, ['latitude', 'longitude']]
            delivery_df = all_points_df.loc[all_points_df['id'] == point2, ['latitude', 'longitude']]

            latitude1 = pickup_df['latitude'].values[0]
            longitude1 = pickup_df['longitude'].values[0]
            latitude2 = delivery_df['latitude'].values[0]
            longitude2 = delivery_df['longitude'].values[0]

            d = hs.haversine((latitude1, longitude1), (latitude2, longitude2))
            distance[point1, point2] = d

# Creating a dictionary of costs of going from pickup point i to delivery point j using vehicle k
# For the moment cost is equal for every
cost = {}
for vehicle in vehicles:
    for (pickup_point, delivery_point), dist in distance.items():
        cost[pickup_point, delivery_point, vehicle] = 0.4*dist

def capacity(vehicle):
    capacity = vehicles_df.loc[vehicles_df['id'] == vehicle, 'capacity'].values[0]
    return capacity

print(f"Running instance with {num_clients} clients")
print("Vehicles: ", vehicles)
print("Pickup Points: ", pickup_points)
print("Delivery Points: ",delivery_points)
print("Starting depot: ", depots[0])
print("Ending depot: ", depots[1])
print("All points: ", all_points)
print("Points no depots: ", points_no_depots)
print("Set1: ", set1)
print("Set2: ", set2)
print("Demands: ",demand)
print("Service times: ", service_time)
print("Distances: ", distance)
print("Costs: ", cost)
print("Max distance = ", round(max(distance.values()), 2), "km")
print("Min distance = ", min(distance.values()), "km")

# Visualize points on an interactive map
map_plot(pickup_points_df, delivery_points_df, depots_df)

