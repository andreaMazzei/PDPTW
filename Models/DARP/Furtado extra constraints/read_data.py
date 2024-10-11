import copy
import pandas as pd

def pair_clients(delivery_points, companies):
    associated_company = {}
    # Ideal clients per company
    clients_per_company = len(delivery_points) // len(companies)
    # Clients that can't be divided evenly
    leftover_clients = len(delivery_points) % len(companies)

    start_index = 0
    for company in companies:
        end_index = start_index + clients_per_company
        if leftover_clients > 0:
            end_index += 1  # Assign one extra client to balance
            leftover_clients -= 1

        company_clients = delivery_points[start_index:end_index]  # Get clients for this company
        for client in company_clients:
            associated_company[client] = company

        start_index = end_index  # Move to the next batch of clients

    return associated_company


def read_file(filename):
    df_data = pd.read_excel(filename, engine="openpyxl",
                                sheet_name='data')

    # Extract variables from the DataFrame
    variables = df_data.set_index('Variable')['Value'].to_dict()

    # Assign variables
    num_clients = variables['num_clients']
    num_companies = variables['num_companies']
    num_vehicles = variables['num_vehicles']
    max_capacity = variables['max_capacity']
    time_horizon = variables['time_horizon']
    max_route_duration = variables['max_route_duration']
    max_ride_time_client = variables['max_ride_time_client']

    print(f"num_clients: {num_clients}")
    print(f"num_companies: {num_companies}")
    print(f"num_vehicles: {num_vehicles} with maximum capacity {max_capacity}")
    print(f"Time horizon: {time_horizon} minutes")
    print(f"max_route_duration: {max_route_duration} minutes")
    print(f"max_ride_time_client: {max_ride_time_client} minutes")

    df_distance = pd.read_excel(filename, engine="openpyxl", sheet_name='distance matrix (km)')
    df_distance = df_distance.iloc[:, 1:]  # Drop first column
    df_distance.columns = range(df_distance.shape[1])  # Rename columns to numerical indices

    df_time = pd.read_excel(filename, engine="openpyxl", sheet_name='time matrix (minutes)')
    df_time = df_time.iloc[:, 1:]  # Drop first column
    df_time.columns = range(df_time.shape[1])  # Rename columns to numerical indices

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

    # Assegnare le company ai clients: creo una lista di dizionari
    # [{'client': 0, 'company': 'Company X'}, {'client': 1, 'company': 'Company X'},.........
    # es client 0  e 2 assegno company 1
    # Io conosco le distaze tra clients (e deposito) e companies dist[client0, company1] = XXX gli indici dei clients e gli indici dei deliveri points
    # Quindi la distanza dist[client, delivery_vertex] = dist[client, company associata al delivery vertex ] -> dist[0,compan] = dist[client 0, company1]
    # e sink
    company_indexes = range(num_clients + 1, num_clients + num_companies + 1)
    associated_company = pair_clients(delivery_points, company_indexes)
    print("Association delivery vertex - companies: ", associated_company)

    distance_client_company = {}
    time_client_company = {}
    for i, row in df_distance.iterrows():
        for j, value in row.items():
            distance_client_company[i, j] = value

    for i, row in df_time.iterrows():
        for j, value in row.items():
            time_client_company[i, j] = value

    distance = {}
    time = {}

    # Distanze prefissate
    distance[source, sink] = 0
    distance[sink, source] = 0

    for p1 in all_points:
        for p2 in all_points:
            if p1 == p2:
                distance[p1, p2] = 0
                distance[p2, p1] = 0
            elif p1 == source and p2 in pickup_points:
                distance[p1,p2] = distance_client_company[p1,p2]
                distance[sink,p2] = distance_client_company[p1,p2]
                distance[p2,p1] = distance_client_company[p2,p1]
                distance[p2,sink] = distance_client_company[p2,p1]
            elif p1 == source and p2 in delivery_points:
                distance[p1,p2] = distance_client_company[p1,associated_company[p2]]
                distance[sink,p2] = distance_client_company[p1,associated_company[p2]]
                distance[p2,p1] = distance_client_company[associated_company[p2],p1]
                distance[p2,sink] = distance_client_company[associated_company[p2],p1]
            if p1 in pickup_points and p2 in pickup_points:
                distance[p1,p2] = distance_client_company[p1,p2]
                distance[p2,p1] = distance_client_company[p2,p1]
            elif p1 in pickup_points and p2 in delivery_points:
                distance[p1,p2] = distance_client_company[p1,associated_company[p2]]
                distance[p2,p1] = distance_client_company[associated_company[p2],p1]
            elif p1 in delivery_points and p2 in delivery_points:
                distance[p1,p2] = distance_client_company[associated_company[p1], associated_company[p2]]

    time[source, sink] = 0
    time[sink, source] = 0

    for p1 in all_points:
        for p2 in all_points:
            if p1 == p2:
                time[p1, p2] = 0
                time[p2, p1] = 0
            elif p1 == source and p2 in pickup_points:
                time[p1,p2] = time_client_company[p1,p2]
                time[sink,p2] = time_client_company[p1,p2]
                time[p2,p1] = time_client_company[p2,p1]
                time[p2,sink] = time_client_company[p2,p1]
            elif p1 == source and p2 in delivery_points:
                time[p1,p2] = time_client_company[p1,associated_company[p2]]
                time[sink,p2] = time_client_company[p1,associated_company[p2]]
                time[p2,p1] = time_client_company[associated_company[p2],p1]
                time[p2,sink] = time_client_company[associated_company[p2],p1]
            if p1 in pickup_points and p2 in pickup_points:
                time[p1,p2] = time_client_company[p1,p2]
                time[p2,p1] = time_client_company[p2,p1]
            elif p1 in pickup_points and p2 in delivery_points:
                time[p1,p2] = time_client_company[p1,associated_company[p2]]
                time[p2,p1] = time_client_company[associated_company[p2],p1]
            elif p1 in delivery_points and p2 in delivery_points:
                time[p1,p2] = time_client_company[associated_company[p1], associated_company[p2]]

    # PER VISUALIZZARLO MEGLIO TRASFORMAZIONE IN DATAFRAME E EXPROT CSV
    # # # Extract coordinates and distances
    # rows = []
    # for (x, y), distance in distance.items():
    #     rows.append({'x': x, 'y': y, 'Distance (km)': distance})
    #
    # # Create the DataFrame
    # df = pd.DataFrame(rows)
    #
    # # Pivot the data for a clearer presentation
    # df_pivot = df.pivot(index='x', columns='y', values='Distance (km)')
    #
    # pd.set_option('display.max_rows', None)  # Display all rows
    # pd.set_option('display.max_columns', None)  # Display all columns
    # print(df_pivot)
    # df_pivot.to_csv('distance_matrix.csv', index=False)  # Save pivoted DataFrame


    cost = {}
    for vehicle in vehicles:
        for (pickup_point, delivery_point), dist in distance.items():
            cost[pickup_point, delivery_point, vehicle] = distance[pickup_point, delivery_point]

    # print("Distances [km]:")
    # print(distance)
    # print("Times [min]:")
    # print(time)
    # print("Cost:")
    # print(cost)

    service_time = {}
    demand = {}
    earliest_time = {}
    latest_time = {}

    df_tw = pd.read_excel(filename, engine="openpyxl",
                                sheet_name='time windows')

    # Create dictionaries with Vertex as the key
    service_time = df_tw.set_index("Vertex")["Service Time"].to_dict()
    demand = df_tw.set_index("Vertex")["Demand"].to_dict()
    earliest_time = df_tw.set_index("Vertex")["Earliest Time"].to_dict()
    latest_time = df_tw.set_index("Vertex")["Latest Time"].to_dict()

    print("Service time:", service_time)
    print("Demand: ", demand)
    print("Earliest time: ", earliest_time)
    print("Latest time: ", latest_time)
    print(f"Tempo medio = {sum(time.values()) / len(time)} minutes")
    print(f"Distanza media = {sum(distance.values()) / len(distance)} km")

    df_geo = pd.read_excel(filename, engine="openpyxl",
                                sheet_name='geocoded addresses')
    df_geo = df_geo[["Latitudine", "Longitudine"]]
    df1 = df_geo.head(1)
    df2 = df_geo.iloc[1:(num_clients + 1)].copy()
    df3 = df_geo.iloc[(num_clients + 1): (2*num_clients+1)].copy()
    from Utilites import show_map
    # show_map.map_plot2(df2, df3, df1)

    return (num_clients, num_companies, num_vehicles, max_capacity, time_horizon, max_route_duration, max_ride_time_client,
            source, sink, vehicles, all_points, points_no_depots, pickup_points, delivery_points, set1, set2, distance,
            cost, time, service_time, demand, earliest_time, latest_time)
