import pandas as pd
from math import sin, cos, sqrt, atan2, radians
from sklearn.neighbors import KNeighborsClassifier

# load resales_combined data and amenities into df

## csvs are omitted from github for space reasons
resales1 = pd.read_csv("resale_combined_amenities_part_1.csv")
resales2 = pd.read_csv("resale_combined_amenities_part_2.csv")
resales3 = pd.read_csv("resale_combined_amenities_part_3.csv")
resales4 = pd.read_csv("resale_combined_amenities_part_4.csv")
resales5 = pd.read_csv("resale_combined_amenities_part_5.csv")
resales6 = pd.read_csv("resale_combined_amenities_part_6.csv")
resales7 = pd.read_csv("resale_combined_amenities_part_7.csv")
resales8 = pd.read_csv("resale_combined_amenities_part_8.csv")
resales9 = pd.read_csv("resale_combined_amenities_part_9.csv")
resales10 = pd.read_csv("resale_combined_amenities_part_10.csv")
resales11 = pd.read_csv("resale_combined_amenities_part_11.csv")
resales12 = pd.read_csv("resale_combined_amenities_part_12.csv")
resales13 = pd.read_csv("resale_combined_amenities_part_13.csv")
resales14 = pd.read_csv("resale_combined_amenities_part_14.csv")
resales15 = pd.read_csv("resale_combined_amenities_part_15.csv")

resales_combined = pd.concat([resales1, resales2, resales3, resales4, resales5, resales6, resales7, resales8, resales9, resales10, resales11, resales12, resales13, resales14, resales15], axis=0, ignore_index=True)

amenities = pd.read_csv('amenities.csv')
resale_combined_malls_hawkers_supermarkets_amenities = resales_combined.copy()

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
knn = KNeighborsClassifier(n_neighbors=1, algorithm='auto', metric=earth_distance)

# Fit model with amenity locations
knn.fit(amenities[['lat', 'lng']], amenities['amenity_name'])

# Find nearest amenity for each resale record
nearest_amenity = knn.predict(resales_combined[['lat', 'lng']])
nearest_amenity_dist = knn.kneighbors(resales_combined[['lat', 'lng']])[0][:, 0]

# Add the nearest amenity and distance
resale_combined_malls_hawkers_supermarkets_amenities['nearest_amenity'] = nearest_amenity
resale_combined_malls_hawkers_supermarkets_amenities['nearest_amenity_dist'] = nearest_amenity_dist

resale_combined_malls_hawkers_supermarkets_amenities.to_csv('resale_combined_malls_hawkers_supermarkets_amenities.csv', index=False)
