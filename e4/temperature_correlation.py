import sys
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt


def get_cities_data(file):
    """
    Create cities data frame with following steps:

    1. Drop records with missing population or area 
    2. Convert area from m² to km²
    3. Compute density
    4. Filter records with area > 10000 km²
    """

    data = pd.read_csv(file).dropna(subset=['area', 'population'])
    data['area'] = data['area'] / 1000000
    data['density'] = data['population']/data['area']
    data = data[data['area'] <= 10000]

    return data


def get_stations_data(file):
    """
    Create a stations data frame and divide 'avg_tmax' by 10 
    as it is given as °C×10.
    """

    data = pd.read_json(file, lines=True)
    data['avg_tmax'] = np.divide(data['avg_tmax'], 10)

    return data


# haversine funcrtion implemented from:
# https://stackoverflow.com/questions/4913349/haversine-formula-in-python-bearing-and-distance-between-two-gps-points
def haversine(lon1, lat1, lon2, lat2):
    """
    Calculate the great circle distance between two points
    on the earth (specified in decimal degrees)

    All args must be of equal length.    

    """
    lon1, lat1, lon2, lat2 = map(np.radians, [lon1, lat1, lon2, lat2])

    dlon = lon2 - lon1
    dlat = lat2 - lat1

    a = np.sin(dlat/2.0)**2 + np.cos(lat1) * np.cos(lat2) * np.sin(dlon/2.0)**2

    R = 6371
    c = 2 * np.arcsin(np.sqrt(a))
    m = 1000 * R * c

    return m


def distance(city, stations):
    """
    Calculate the distance between one city and every station.
    """

    return haversine(
        city['longitude'],
        city['latitude'],
        stations['longitude'],
        stations['latitude']
    )


def best_tmax(city, stations):
    nearest_station = pd.Series.idxmin(distance(city, stations))
    return stations.iloc[nearest_station]['avg_tmax']


def plot(tmax, density, output):
    """
    Create a scatterplot of average maximum temperature
    against population density.
    """

    plt.title('Temperature vs Population Density')
    plt.xlabel('Avg Max Temperature (\u00b0C)')
    plt.ylabel('Population Density (people/km\u00b2)')
    plt.scatter(tmax, density, c='b')
    plt.savefig(output)


def main():
    stations_file = sys.argv[1]
    cities_file = sys.argv[2]
    output = sys.argv[3]

    stations = get_stations_data(stations_file)
    cities = get_cities_data(cities_file)
    best_tmax_per_city = cities.apply(best_tmax, stations=stations, axis=1)

    plot(
        best_tmax_per_city,
        cities['density'],
        output
    )

    return 0


if __name__ == "__main__":
    main()
