import pandas as pd
from math import sin, cos, sqrt, atan2, radians
from sklearn.neighbors import NearestNeighbors

# load schools.csv into df
schools = pd.read_csv('schools.csv')
# rename latitude and longitude to lat and lng
schools.rename(columns={'latitude': 'lat', 'longitude': 'lng'}, inplace=True)

# load resales data into df
path = '../../data/cleaned_data/resales_processed_'
resales1 = pd.read_csv(path + "aa")
resales2 = pd.read_csv(path + "ab")
resales3 = pd.read_csv(path + "ac")
resales4 = pd.read_csv(path + "ad")
resales5 = pd.read_csv(path + "ae")

columns = resales1.columns
for df in [resales2, resales3, resales4, resales5]:
    df.columns = columns

resales = pd.concat([resales1, resales2, resales3, resales4, resales5], axis=0, ignore_index=True)

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
knn = NearestNeighbors(n_neighbors=1, algorithm='brute', metric=earth_distance)

knn.fit(schools[['lat', 'lng']])

distances, indices = knn.kneighbors(resales[['lat', 'lng']])

resales['nearest_school_dist'] = distances
resales['nearest_school'] = schools['school_name'].iloc[indices.flatten()].values

# save into cleaned_data
resales.to_csv('../../data/cleaned_data/resales_processed.csv', index=False)
