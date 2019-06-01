from pykalman import KalmanFilter
from xml.dom.minidom import getDOMImplementation

import sys
import pandas as pd
import numpy as np
import xml.dom.minidom


def get_data(filename):
    # Parsing xml data
    doc = xml.dom.minidom.parse(filename)
    lon_lats = pd.Series(doc.getElementsByTagName('trkpt'))

    # Creating data frame
    points = pd.DataFrame()
    points['lat'] = lon_lats.apply(lambda x: float(x.getAttribute('lat')))
    points['lon'] = lon_lats.apply(lambda x: float(x.getAttribute('lon')))

    return points


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


def distance(points):
    points_shifted = points.shift(periods=1)

    distances = haversine(
        points['lon'],
        points['lat'],
        points_shifted['lon'],
        points_shifted['lat']
    )

    return np.sum(distances)


def smooth(points):
    # Preparing Kalman filter parameters
    initial_state = points.iloc[0]
    observation_covariance = np.diag([0.35, 0.35]) ** 2
    transition_covariance = np.diag([0.25, 0.25]) ** 2
    transition = [[1, 0], [0, 1]]

    # Creating Kalman filter
    kf = KalmanFilter(
        initial_state_mean=initial_state,
        initial_state_covariance=observation_covariance,
        observation_covariance=observation_covariance,
        transition_covariance=transition_covariance,
        transition_matrices=transition
    )

    kalman_smoothed, _ = kf.smooth(points)
    smoothed_dataframe = pd.DataFrame(kalman_smoothed, columns=['lat', 'lon'])

    return smoothed_dataframe


def output_gpx(points, output_filename):
    """
    Output a GPX file with latitude and longitude from the points DataFrame.
    """

    def append_trkpt(pt, trkseg, doc):
        trkpt = doc.createElement('trkpt')
        trkpt.setAttribute('lat', '%.8f' % (pt['lat']))
        trkpt.setAttribute('lon', '%.8f' % (pt['lon']))
        trkseg.appendChild(trkpt)

    doc = getDOMImplementation().createDocument(None, 'gpx', None)
    trk = doc.createElement('trk')
    doc.documentElement.appendChild(trk)
    trkseg = doc.createElement('trkseg')
    trk.appendChild(trkseg)

    points.apply(append_trkpt, axis=1, trkseg=trkseg, doc=doc)

    with open(output_filename, 'w') as fh:
        doc.writexml(fh, indent=' ')


def main():
    points = get_data(sys.argv[1])
    print('Unfiltered distance: %0.2f' % (distance(points),))

    smoothed_points = smooth(points)
    print('Filtered distance: %0.2f' % (distance(smoothed_points),))
    output_gpx(smoothed_points, 'out.gpx')


if __name__ == '__main__':
    main()
