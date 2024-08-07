import pandas as pd
import requests
import time

# Read csv files

path = "../../data/original_resale_data/"

resale1 = pd.read_csv(f"{path}1ResaleFlatPricesBasedonApprovalDate19901999.csv")
resale2 = pd.read_csv(f"{path}2ResaleFlatPricesBasedonApprovalDate2000Feb2012.csv")
resale3 = pd.read_csv(f"{path}3ResaleFlatPricesBasedonRegistrationDateFromMar2012toDec2014.csv")
resale4 = pd.read_csv(f"{path}4ResaleFlatPricesBasedonRegistrationDateFromJan2015toDec2016.csv")
resale5 = pd.read_csv(f"{path}5ResaleflatpricesbasedonregistrationdatefromJan2017onwards.csv")

# Merge all csv files into a single dataframe
resale = pd.concat([resale1, resale2, resale3,resale4, resale5], ignore_index=True)
resale = resale.map(lambda x: x.strip() if isinstance(x, str) else x)

# Regularising addresses
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

# Apply the function to the street_name column
resale['street_name'] = resale['street_name'].apply(replace)

# Create address list for OneMap API
resale['blk + street_name'] = resale['block'] + ' ' + resale['street_name']
addresslist = list(resale['blk + street_name'])
addresslist = list(set(addresslist))

# Function for fetching location features from OneMap
def getcoordinates(address):
    req = requests.get('https://www.onemap.gov.sg/api/common/elastic/search?searchVal='+address+'&returnGeom=Y&getAddrDetails=Y&pageNum=1')
    resultsdict = eval(req.text)
    if len(resultsdict['results'])>0:
        return resultsdict['results'][0]['LATITUDE'], resultsdict['results'][0]['LONGITUDE'], resultsdict['results'][0]['BUILDING'], resultsdict['results'][0]['SEARCHVAL'], resultsdict['results'][0]['POSTAL']
    else:
        pass

# Fetch location features
coordinateslist = []
count = 0
failed_count = 0
for address in addresslist:
    try:
        if len(getcoordinates(address)) > 0:
            count += 1
            print('Extracting', count, 'out of', len(addresslist), 'addresses')
            coordinateslist.append(getcoordinates(address))
    except:
        count += 1
        failed_count += 1
        print('Failed to extract', failed_count, 'out of', len(addresslist), 'addresses')
        coordinateslist.append(None)
    if count % 200 == 0:
        print('Pausing for 20 seconds...')
        time.sleep(20)

print('Total Number of Addresses With No Coordinates:', failed_count)


# # Didn't use this in the end because this line "result_exact_match = list(filter(lambda x: address in x['ADDRESS'], result)) would cause more requests to fail

# def getcoordinates(addresses):
#     coordinateslist = []
#     count = 0
#     failed_count = 0
#     for address in addresses:
#         url = f'https://www.onemap.gov.sg/api/common/elastic/search?searchVal={address}&returnGeom=Y&getAddrDetails=Y&pageNum=1'
#         response = requests.request('GET',url)
#         result = response.json()['results']
#         if result:
#             count += 1
#             print('Extracting', count, 'out of', len(addresses), 'addresses')
#             result_exact_match = list(filter(lambda x: address in x['ADDRESS'], result))
#             latitude = result_exact_match[0].get('LATITUDE', None)
#             longitude = result_exact_match[0].get('LONGITUDE', None)
#             building = result_exact_match[0].get('BUILDING', None)
#             search_val = result_exact_match[0].get('SEARCHVAL', None)
#             postal = result_exact_match[0].get('POSTAL', None)
#             coordinateslist.append((latitude, longitude, building, search_val, postal))
#         else:
#             count += 1
#             failed_count += 1
#             print('Failed to extract', failed_count, 'out of', len(addresses), 'addresses')
#             coordinateslist.append(None)
#         if count % 200 == 0:
#             print('Pausing for 20 seconds...')
#             time.sleep(20)
#     print('Total Number of Addresses With No Coordinates:', failed_count)
#     return coordinateslist


# Merge location features with address list
df_coordinates = pd.DataFrame(coordinateslist)
df_coordinates.rename(columns={0:'lat', 1:'lng', 2:'building', 3:'address', 4:'postal'}, inplace=True)

addresslist = pd.DataFrame(addresslist)
addresslist.rename(columns={0:'blk + street_name'}, inplace=True)

df_coordinates = pd.concat([addresslist, df_coordinates],axis=1)

# A second run was carried out for the addresses without coordinates to make sure OneMap dosen't miss out on any address errorneously
df_coordinates2 = df_coordinates[df_coordinates['lat'].isnull() & df_coordinates['lng'].isnull()]
addresslist2 = list(df_coordinates2['blk + street_name'])

coordinateslist2= []
count2 = 0
failed_count2 = 0
for address in addresslist2:
    try:
        if len(getcoordinates(address))>0:
            count2 = count2 + 1
            print('Extracting',count2,'out of',len(addresslist2),'addresses')
            coordinateslist2.append(getcoordinates(address))
    except:
        count2 = count2 + 1
        failed_count2 = failed_count2 + 1
        print('Failed to extract',failed_count2,'out of',len(addresslist2),'addresses')
        coordinateslist2.append(None)
print('Total Number of Addresses With No Coordinates',failed_count2)

# Merge location features 2 with address list 2
padded_list = [[None] * 5 if lst is None else lst for lst in coordinateslist2]
df_coordinates2 = pd.DataFrame(padded_list)
df_coordinates2.rename(columns={0:'lat', 1:'lng', 2:'building', 3:'address', 4:'postal'}, inplace=True)

addresslist2 = pd.DataFrame(addresslist2)
addresslist2.rename(columns={0:'blk + street_name'}, inplace=True)
df_coordinates2 = pd.concat([addresslist2, df_coordinates2],axis=1)
df_coordinates2.dropna(inplace=True)

# Merge the 2 location data frames and clean up
df_coordinates.dropna(inplace=True)
df_coordinates_combined = pd.concat([df_coordinates, df_coordinates2], ignore_index=True)

# Write final location features to csv file
# df_coordinates_combined.to_csv('coordinates_OneMapAPI_final.csv', index=False)

# Merge resale data with location features and clean up
resale_with_coordinates = pd.merge(resale, df_coordinates_combined[['blk + street_name','lat', 'lng','building', 'address', 'postal']], on=['blk + street_name'], how='left')
resale_with_coordinates.drop(columns = 'blk + street_name', inplace=True)
resale_with_coordinates.dropna(subset=['lat', 'lng'], inplace=True)

# Write imputed resale data to csv file
# resale_with_coordinates.to_csv('resale_with_coordinates.csv', index=False)

# List of stations in Singapore (compiled from https://www.lta.gov.sg/content/ltagov/en/map/train.html)
train_stations = pd.read_csv('stations.csv')
stationlist = list(train_stations['station_name'])

# Fetch location features of the stations
station_coordinateslist = []
station_count = 0
station_failed_count = 0
for station in stationlist:
    try:
        if len(getcoordinates(station)) > 0:
            station_count += 1
            print('Extracting', station_count, 'out of', len(stationlist), 'stations')
            station_coordinateslist.append(getcoordinates(station))
    except:
        station_count += 1
        station_failed_count += 1
        print('Failed to extract', station_failed_count, 'out of', len(stationlist), 'stations')
        station_coordinateslist.append(None)
    if station_count % 50 == 0:
        print('Pausing for 20 seconds...')
        time.sleep(20)

print('Total Number of Stations With No Coordinates:', station_failed_count)

# Merge location features with station list and clean up
df_station_coordinateslist = pd.DataFrame(station_coordinateslist)
df_station_coordinateslist.rename(columns={0:'lat', 1:'lng', 2:'building', 3:'address', 4:'postal'}, inplace=True)
stationlist = pd.DataFrame(stationlist)
stationlist.rename(columns={0:'station_name'}, inplace=True)
train_stations = pd.concat([stationlist, df_station_coordinateslist],axis=1)

train_stations = train_stations.drop_duplicates(subset=['lat', 'lng'], keep='first')
train_stations = train_stations.drop(columns=['station_name', 'address'])
train_stations = train_stations.rename(columns={'building': 'station_name'})

train_stations.to_csv('train_stations_OneMapAPI.csv', index=False)

# Function to compute the distance between two geolocations
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
nearest_station = knn.predict(resale_with_coordinates[['lat', 'lng']])
station_dist = knn.kneighbors(resale_with_coordinates[['lat', 'lng']])[0][:, 0]

# Populate nearest MRT station and distance columns
resale_with_coordinates['nearest_station'] = nearest_station
resale_with_coordinates['station_dist'] = station_dist

resale_with_coordinates.to_csv('resale_with_lat_stations.csv', index=False)


# # Realised OneMap API results for 52/54 KENT RD, 2/4/6/7/8/10/11 JLN BATU are incorrect after displaying train stations serving Kallang/Whampoa Town

# # Regularise street names (Manipulation of Jln Bata and Kent Rd didn't work)
# def replace(text):
#     # Create a dictionary mapping of replacements
#     replacements = {'BT ': 'BUKIT ', 'UPP' : 'UPPER', 'C\'WEALTH' : 'COMMONWEALTH', 'ST.' : 'SAINT', 'KG' : 'KAMPONG', \
#                     'PK' : 'PARK', 'LOR' : 'LORONG', 'TG' : 'TANJONG', 'SIMS PL' : 'SIMS PLACE', 'DOVER CL EAST' : 'DOVER CRESCENT EAST', \
#                     'KIM TIAN PL' : 'KIM TIAN PLACE', 'KEAT HONG CL' : 'KEAT HONG CLOSE', 'QUEEN\'S CL' : 'QUEEN\'S CLOSE', \
#                     'PINE CL' : 'PINE CLOSE', 'CANTONMENT CL' : 'CANTONMENT CLOSE', 'REDHILL CL' : 'REDHILL CLOSE', \
#                     'PUNGGOL PL' : 'PUNGGOL PLACE', 'HOLLAND CL' : 'HOLLAND CLOSE', 'SEMBAWANG CL' : 'SEMBAWANG CLOSE', \
#                     'COMMONWEALTH CL' : 'COMMONWEALTH CLOSE', 'BOON LAY PL' : 'BOON LAY PLACE','52 KENT RD' : '52 KENT VILLE', '54 KENT RD' : '54 KENT VILLE', \
#                     '2 JALAN BATU' : '2 JALAN BATU DI', '4 JALAN BATU' : '4 JLN BATU DI','6 JALAN BATU' : '6 JLN BATU DI','7 JALAN BATU' : '7 JLN BATU DI',\
#                     '8 JALAN BATU' : '8 JLN BATU DI', '10 JALAN BATU' : '10 JLN BATU DI', '11 JALAN BATU' : '11 JLN BATU DI'}

#     # Iterate over the dictionary and replace each key with its corresponding value
#     for key, value in replacements.items():
#         text = text.replace(key, value)
#     return text

# # Apply the function to the street_name column
# resale['street_name'] = resale['street_name'].apply(replace)
