import random
import pandas as pd

num_points = 20

# min_latitude = 44.5
# max_latitude = 44.8
# min_longitude = 10.4
# max_longitude = 10.8

min_latitude = 44.642971
max_latitude = 44.754448
min_longitude = 10.52412
max_longitude = 10.735404

def generate_pickup_points(num_points, min_lat, max_lat, min_long, max_long):

    # Generate random coordinates
    latitudes = [random.uniform(min_lat, max_lat) for _ in range(num_points)]
    longitudes = [random.uniform(min_long, max_long) for _ in range(num_points)]

    # Assign IDs
    ids = list(range(1, num_points + 1))

    # Create DataFrame
    df = pd.DataFrame({'id': ids, 'latitude': latitudes, 'longitude': longitudes})
    df.to_csv('pickup_points.csv', index=False)
    return df

def generate_delivery_points(num_points, min_lat, max_lat, min_long, max_long):

    # Generate random coordinates
    latitudes = [random.uniform(min_lat, max_lat) for _ in range(num_points)]
    longitudes = [random.uniform(min_long, max_long) for _ in range(num_points)]

    # Assign IDs
    ids = list(range(num_points + 1, 2*num_points + 1))

    # Create DataFrame
    df = pd.DataFrame({'id': ids, 'latitude': latitudes, 'longitude': longitudes})
    df.to_csv('prova.csv', index=False)
    return df

generate_pickup_points(num_points, min_latitude, max_latitude, min_longitude, max_longitude)
generate_delivery_points(num_points, min_latitude, max_latitude, min_longitude, max_longitude)
