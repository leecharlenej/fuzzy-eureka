import pandas as pd
from math import sin, cos, sqrt, atan2, radians
from sklearn.neighbors import KNeighborsClassifier

# load rental data and earlier extracted HDB coordinates into df
rental = pd.read_csv("RentingOutofFlats.csv" )
rental = rental.map(lambda x: x.strip() if isinstance(x, str) else x)
df_coordinates_combined = pd.read_csv("coordinates_OneMapAPI_final.csv")
rental_with_coordinates = rental.copy()

# Regularise street names
def replace(text):
    replacements = {'BT ': 'BUKIT ', 'UPP' : 'UPPER', 'C\'WEALTH' : 'COMMONWEALTH', 'ST.' : 'SAINT', 'KG' : 'KAMPONG', \
                    'PK' : 'PARK', 'LOR' : 'LORONG', 'TG' : 'TANJONG', 'SIMS PL' : 'SIMS PLACE', 'DOVER CL EAST' : 'DOVER CRESCENT EAST', \
                    'KIM TIAN PL' : 'KIM TIAN PLACE', 'KEAT HONG CL' : 'KEAT HONG CLOSE', 'QUEEN\'S CL' : 'QUEEN\'S CLOSE', \
                    'PINE CL' : 'PINE CLOSE', 'CANTONMENT CL' : 'CANTONMENT CLOSE', 'REDHILL CL' : 'REDHILL CLOSE', \
                    'PUNGGOL PL' : 'PUNGGOL PLACE', 'HOLLAND CL' : 'HOLLAND CLOSE', 'SEMBAWANG CL' : 'SEMBAWANG CLOSE', \
                    'COMMONWEALTH CL' : 'COMMONWEALTH CLOSE', 'BOON LAY PL' : 'BOON LAY PLACE'}
    for key, value in replacements.items():
        text = text.replace(key, value)
    return text

rental_with_coordinates['street_name'] = rental_with_coordinates['street_name'].apply(replace)


rental_with_coordinates['blk + street_name'] = rental_with_coordinates['block'] + ' ' + rental_with_coordinates['street_name']
rental_with_coordinates = pd.merge(rental_with_coordinates, df_coordinates_combined[['blk + street_name', 'lat', 'lng','building', 'postal']], on=['blk + street_name'], how='left')
rental_with_coordinates = rental_with_coordinates.dropna(subset= ['lat', 'lng'])
rental_with_coordinates.to_csv('rental_with_coordinates.csv', index=False)

# earth distance function
def earth_distance(x, y):
  R = 6373.0

  lat1, lng1 = radians(x[0]), radians(x[1])
  lat2, lng2 = radians(y[0]), radians(y[1])

  dlon = lng2 - lng1
  dlat = lat2 - lat1

  a = sin(dlat / 2)**2 + cos(lat1) * cos(lat2) * sin(dlon / 2)**2
  c = 2 * atan2(sqrt(a), sqrt(1 - a))
  return R * c

# Create a KNeighborsClassifier model
knn = KNeighborsClassifier(n_neighbors=1, algorithm='brute', metric=earth_distance)
knn.fit(train_stations[['lat', 'lng']], train_stations['station_name'])

# Find nearest train station and distance for each rental record
nearest_station_rental = knn.predict(rental_with_coordinates[['lat', 'lng']])
station_dist_rental = knn.kneighbors(rental_with_coordinates[['lat', 'lng']])[0][:, 0]

# Add the nearest train station and nearest train distance
rental_with_coordinates['nearest_station'] = nearest_station_rental
rental_with_coordinates['station_dist'] = station_dist_rental

rental_with_coordinates.drop(columns = 'blk + street_name', inplace=True)
rental_with_coordinates.to_csv('rental_with_lat_stations.csv', index=False)


rentals_with_lat_malls = rental_with_coordinates.copy()

# Fit model with mall locations
knn.fit(malls[['lat', 'lng']], malls['mall_name'])

# Find nearest mall for each rental record
nearest_mall_rental = knn.predict(rentals_with_lat_malls[['lat', 'lng']])
mall_dist_rental = knn.kneighbors(rentals_with_lat_malls[['lat', 'lng']])[0][:, 0]

# Add the nearest Mall and distance
rentals_with_lat_malls['nearest_mall'] = nearest_mall_rental
rentals_with_lat_malls['mall_dist'] = mall_dist_rental

rentals_with_lat_malls.to_csv('rental_with_lat_malls.csv', index=False)


rentals_with_lat_malls_hawkers = rentals_with_lat_malls.copy()

# Fit model with hawker locations
knn.fit(hawkers_lat_lng[['lat', 'lng']], hawkers_lat_lng['hawker_name'])

# Find nearest hawker for each rental record
nearest_hawker_rental = knn.predict(rentals_with_lat_malls_hawkers[['lat', 'lng']])
hawker_dist_rental = knn.kneighbors(rentals_with_lat_malls_hawkers[['lat', 'lng']])[0][:, 0]

# Add the nearest hawker and distance
rentals_with_lat_malls_hawkers['nearest_hawker'] = nearest_hawker_rental
rentals_with_lat_malls_hawkers['hawker_dist'] = hawker_dist_rental

rentals_with_lat_malls_hawkers.to_csv('rental_with_lat_stations_malls_hawkers.csv', index=False)

rentals_with_lat_stations_malls_hawkers_supermarkets = rentals_with_lat_malls_hawkers.copy()

# Fit model with supermarket locations
knn.fit(supermarkets_lat_lng[['lat', 'lng']], supermarkets_lat_lng['supermarket_street'])

# Find nearest supermarket for each rental record
nearest_supermarket_rental = knn.predict(rentals_with_lat_stations_malls_hawkers_supermarkets[['lat', 'lng']])
supermarket_dist_rental = knn.kneighbors(rentals_with_lat_stations_malls_hawkers_supermarkets[['lat', 'lng']])[0][:, 0]

# Add the nearest supermarket and distance
rentals_with_lat_stations_malls_hawkers_supermarkets['nearest_supermarket'] = nearest_supermarket_rental
rentals_with_lat_stations_malls_hawkers_supermarkets['supermarket_dist'] = supermarket_dist_rental

rentals_with_lat_stations_malls_hawkers_supermarkets.to_csv('rental_with_lat_stations_malls_hawkers_supermarkets.csv', index=False)


rentals_with_lat_stations_malls_hawkers_supermarkets_amenities = rentals_with_lat_stations_malls_hawkers_supermarkets.copy()

# Fit model with amenity locations
knn.fit(amenities[['lat', 'lng']], amenities['amenity_name'])

# Find nearest amenity for each rental record
nearest_amenity_rental = knn.predict(rentals_with_lat_stations_malls_hawkers_supermarkets_amenities[['lat', 'lng']])
amenity_dist_rental = knn.kneighbors(rentals_with_lat_stations_malls_hawkers_supermarkets_amenities[['lat', 'lng']])[0][:, 0]

# Add the nearest amenity and distance
rentals_with_lat_stations_malls_hawkers_supermarkets_amenities['nearest_amenity'] = nearest_amenity_rental
rentals_with_lat_stations_malls_hawkers_supermarkets_amenities['amenity_dist'] = amenity_dist_rental

rentals_with_lat_stations_malls_hawkers_supermarkets_amenities.to_csv('rental_with_lat_stations_malls_hawkers_supermarkets_amenities.csv', index=False)


rentals_with_lat_stations_malls_hawkers_supermarkets_amenities_schools = rentals_with_lat_stations_malls_hawkers_supermarkets_amenities.copy()

# Fit model with school locations
knn.fit(schools[['lat', 'lng']], schools['school_name'])

# Find nearest school for each rental record
nearest_school_rental = knn.predict(rentals_with_lat_stations_malls_hawkers_supermarkets_amenities_schools[['lat', 'lng']])
school_dist_rental = knn.kneighbors(rentals_with_lat_stations_malls_hawkers_supermarkets_amenities_schools[['lat', 'lng']])[0][:, 0]

# Add the nearest school and distance
rentals_with_lat_stations_malls_hawkers_supermarkets_amenities_schools['nearest_school'] = nearest_school_rental
rentals_with_lat_stations_malls_hawkers_supermarkets_amenities_schools['school_dist'] = school_dist_rental

rentals_with_lat_stations_malls_hawkers_supermarkets_amenities_schools.to_csv('rental_with_lat_stations_malls_hawkers_supermarkets_amenities_schools.csv', index=False)


