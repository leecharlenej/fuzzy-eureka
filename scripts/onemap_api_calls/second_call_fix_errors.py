# Note: This script is used to fix the errors in the first call to the OneMap API. Specifically, we found that the Kent Road and Jalan Batu addresses were not mapped to the right addresses by OneMap.


import pandas as pd
import numpy as np
import requests

### UPDATE KENT ROAD AND JALAN BATU ADDRESSES ###

# load the data
old_resales = pd.read_csv('resale_with_lat_stations.csv')

# create a new column to store the block and street name
old_resales['blk + street_name'] = old_resales['block'] + ' ' + old_resales['street_name']

# find addresses with kent road and jln batu in one dataframe
kent_road = old_resales[old_resales['street_name'] == 'KENT RD']
jln_batu = old_resales[old_resales['street_name'] == 'JLN BATU']

# unique addresses
kent_road_addresses = set(kent_road['blk + street_name'])
jln_batu_addresses = set(jln_batu['blk + street_name'])

# to store the results to update
results_to_update = []

# iterate through kent road and jln batu addresses, obtain the right vals and store in results_to_update
for address in kent_road_addresses:
    req = requests.get('https://www.onemap.gov.sg/api/common/elastic/search?searchVal='+address+'&returnGeom=Y&getAddrDetails=Y&pageNum=1')
    resultsdict = eval(req.text)
    for result in resultsdict['results']:
        if "KENT ROAD" in result['ROAD_NAME']:
            results_to_update.append({'address': result['ADDRESS'],
                                        'building': result['BUILDING'],
                                        'postal': result['POSTAL'],
                                        'lat': result['LATITUDE'],
                                        'lng': result['LONGITUDE'],
                                        'blk + street_name': address})
            break

for address in jln_batu_addresses:
    req = requests.get('https://www.onemap.gov.sg/api/common/elastic/search?searchVal='+address+'&returnGeom=Y&getAddrDetails=Y&pageNum=1')
    resultsdict = eval(req.text)
    for result in resultsdict['results']:
            if "JALAN BATU DI TANJONG RHU" in result['ADDRESS']:
                results_to_update.append({'address': result['ADDRESS'],
                                            'building': result['BUILDING'],
                                            'postal': result['POSTAL'],
                                            'lat': result['LATITUDE'],
                                            'lng': result['LONGITUDE'],
                                            'blk + street_name': address})
                break

# replace address, building, postal, lat and long in old_resales if blk + street_name matches
for result in results_to_update:
    old_resales.loc[old_resales['blk + street_name'] == result['blk + street_name'], 'address'] = result['address']
    old_resales.loc[old_resales['blk + street_name'] == result['blk + street_name'], 'building'] = result['building']
    old_resales.loc[old_resales['blk + street_name'] == result['blk + street_name'], 'postal'] = result['postal']
    old_resales.loc[old_resales['blk + street_name'] == result['blk + street_name'], 'lat'] = result['lat']
    old_resales.loc[old_resales['blk + street_name'] == result['blk + street_name'], 'lng'] = result['lng']


### UPDATING MRT LOCATION DATA ###

# obtain the vals again to update mrt location data
to_update_mrts = old_resales[(old_resales["street_name"] == "KENT RD") | (old_resales["street_name"] == "JLN BATU")]

# import train stations location data
train_stations = pd.read_csv('train_stations_OneMapAPI.csv')


### KNN TO FIND NEAREST STATION ###

# Function to compute the distance between two geolocations -- all taken from first_call_main.py
from math import sin, cos, sqrt, atan2, radians

def earth_distance(x, y):
  R = 6373.0

  lat1, lng1 = radians(x[0]), radians(x[1])
  lat2, lng2 = radians(y[0]), radians(y[1])

  dlon = lng2 - lng1
  dlat = lat2 - lat1

  a = sin(dlat / 2)**2 + cos(lat1) * cos(lat2) * sin(dlon / 2)**2
  c = 2 * atan2(sqrt(a), sqrt(1 - a))
  return R * c

# For each resale record, find nearest train station and the distance from it
from sklearn.neighbors import KNeighborsClassifier

# Create a KNeighborsClassifier model
knn = KNeighborsClassifier(n_neighbors=1, algorithm='brute', metric=earth_distance)

# Fit model with station locations
knn.fit(train_stations[['lat', 'lng']], train_stations['station_name'])

# Find nearest station for each resale record
nearest_station = knn.predict(to_update_mrts[['lat', 'lng']])
station_dist = knn.kneighbors(to_update_mrts[['lat', 'lng']])[0][:, 0]

# Populate nearest MRT station and distance columns
to_update_mrts['nearest_station'] = nearest_station
to_update_mrts['station_dist'] = station_dist


### UPDATE THE DATAFRAME ###

# use to_update_mrts to update old_resales
for index, row in to_update_mrts.iterrows():
    old_resales.loc[index, 'nearest_station'] = row['nearest_station']
    old_resales.loc[index, 'station_dist'] = row['station_dist']

# drop blk + street_name for cleanup
final_resales = old_resales.drop(columns=['blk + street_name'])

# save into resales_after_api_final.csv
final_resales.to_csv('resales_after_api_final.csv', index=False)

# delete resale_with_lat_stations.csv
import os
os.remove('resale_with_lat_stations.csv')
