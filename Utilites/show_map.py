import plotly.express as px
import pandas as pd

def map_plot(pickup_points, delivery_points, depots):
    """
    Plot a map of pickup and delivery points
    :param pickup_points: dataframe with pickup points
    :param delivery_points: dataframe with delivery points
    """

    # Create a scattermapbox plot with pickup points
    fig = px.scatter_mapbox(pickup_points, lat="latitude", lon="longitude", zoom=10,
                            color_discrete_sequence=['blue'], hover_data=['id'])

    # Add delivery points to the same map
    fig.add_trace(
        px.scatter_mapbox(delivery_points, lat="latitude", lon="longitude",
                          color_discrete_sequence=['red'], hover_data=['id']).data[0]
    )

    # Add depots to the same map
    fig.add_trace(
        px.scatter_mapbox(depots, lat="latitude", lon="longitude",
                          color_discrete_sequence=['green'], hover_data=['id']).data[0]
    )

    # Customize with Plotly options (optional)
    fig.update_layout(mapbox_style="open-street-map")

    # Display the map
    fig.show()

def map_plot2(pickup_points, delivery_points, depots):

    # Create a scattermapbox plot with pickup points
    fig = px.scatter_mapbox(pickup_points, lat="Latitudine", lon="Longitudine", zoom=10,
                            color_discrete_sequence=['blue'])

    # Add delivery points to the same map
    fig.add_trace(
        px.scatter_mapbox(delivery_points, lat="Latitudine", lon="Longitudine",
                          color_discrete_sequence=['red']).data[0]
    )

    # Add depots to the same map
    fig.add_trace(
        px.scatter_mapbox(depots, lat="Latitudine", lon="Longitudine",
                          color_discrete_sequence=['green']).data[0]
    )

    # Customize with Plotly options (optional)
    fig.update_layout(mapbox_style="open-street-map")

    # Display the map
    fig.show()
