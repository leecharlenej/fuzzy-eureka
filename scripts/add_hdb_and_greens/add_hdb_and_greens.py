import pandas as pd
import numpy as np

#################
# LOAD DATASETS #
#################

# load hdbpropertyinfo dataset
hdbpropertyinfo = pd.read_csv('HDBPropertyInformation.csv')

# load resales dataset
path = "../../data/cleaned_data/resales_processed_"
resales_frames = [pd.read_csv(f"{path}{letter}") for letter in
                  ['aa', 'ab', 'ac', 'ad', 'ae', 'af', 'ag', 'ah', 'ai', 'aj']]

columns = resales_frames[0].columns
for df in resales_frames:
    df.columns = columns

resales = pd.concat(resales_frames, axis=0, ignore_index=True)

# load rental dataset
rentals = pd.read_csv('../../data/cleaned_data/rentals_processed.csv')

#######################################################
# ADD MAX FLOOR LEVEL TO RESALES AND RENTALS DATASETS #
#######################################################

# adding fun things

# trying max floor level again

original_resales_length = resales.shape[0]

hdbpropertyinfo = pd.read_csv('HDBPropertyInformation.csv')

resale_streets = set(resales['street_name'].to_list())

# replace street names in hdb dataset to match street names in resale dataset
def replace(text):
    replacements = {'BT ': 'BUKIT ', 'UPP' : 'UPPER', 'C\'WEALTH' : 'COMMONWEALTH', 'ST.' : 'SAINT', 'KG' : 'KAMPONG',
                    'PK' : 'PARK', 'LOR' : 'LORONG', 'TG' : 'TANJONG', 'SIMS PL' : 'SIMS PLACE', 'DOVER CL EAST' : 'DOVER CRESCENT EAST', \
                    'KIM TIAN PL' : 'KIM TIAN PLACE', 'KEAT HONG CL' : 'KEAT HONG CLOSE', 'QUEEN\'S CL' : 'QUEEN\'S CLOSE', \
                    'PINE CL' : 'PINE CLOSE', 'CANTONMENT CL' : 'CANTONMENT CLOSE', 'REDHILL CL' : 'REDHILL CLOSE', \
                    'PUNGGOL PL' : 'PUNGGOL PLACE', 'HOLLAND CL' : 'HOLLAND CLOSE', 'SEMBAWANG CL' : 'SEMBAWANG CLOSE', \
                    'COMMONWEALTH CL' : 'COMMONWEALTH CLOSE', 'BOON LAY PL' : 'BOON LAY PLACE'}

    for key, value in replacements.items():
        text = text.replace(key, value)
    return text

hdbpropertyinfo['street'] = hdbpropertyinfo['street'].apply(replace)
hdbproperties = set(hdbpropertyinfo['street'].to_list())

# check how many addresses belong to streets_not_in_hdbproperties
streets_not_in_hdbproperties = resale_streets - hdbproperties
print('Number of streets in resale dataset not found in hdb dataset:', len(streets_not_in_hdbproperties))
print(streets_not_in_hdbproperties)

# print no of rows where street_name is in streets_not_in_hdbproperties
print(resales[resales['street_name'].isin(streets_not_in_hdbproperties)].shape[0])

# drop these from resale dataset - 300 rows
resales = resales[~resales['street_name'].isin(streets_not_in_hdbproperties)]

d = {}
def get_max_floor_level(row):
    street = row['street']
    blk_no = row['blk_no']
    max_floor_lvl = row['max_floor_lvl']
    d[street] = d.get(street, {})
    d[street][blk_no] = max_floor_lvl

hdbpropertyinfo.apply(get_max_floor_level, axis=1)

blk_count = 0
street_count = 0
no_blk = {}
no_street = []

def add_max_floor_lvl(row):
    street, blk_no = row['street_name'], row['block']
    if street not in d:
        no_street.append(street)
        global street_count
        street_count += 1
        return np.nan
    else:
        if blk_no in d[street]:
            return d[street][blk_no]
        else:
            # check if it ends with a letter, then cut it off
            if blk_no[-1].isalpha():
                blk_no = blk_no[:-1]
                if blk_no in d[street]: # check again
                    return d[street][blk_no]
                else:
                    no_blk[street] = no_blk.get(street, []) + [blk_no]
                    # get the closest blk_no
                    global blk_count
                    blk_count += 1
                    return np.median(list(d[street].values()))
            else:
                # return average
                no_blk[street] = no_blk.get(street, []) + [blk_no]
                blk_count
                blk_count += 1
                return np.median(list(d[street].values()))


# add max_floor_lvl to resale dataset
resales['max_floor_lvl'] = resales.apply(add_max_floor_lvl, axis=1)

print("No. of rows with no street name in hdbpropertyinfo dataset: ", street_count)
print("No of blocks with no record in hdbpropertyinfo dataset: ", blk_count)

# no. of rows removed - 0
print("Number of nan rows for max floor lvl: ", resales['max_floor_lvl'].isna().sum())

# check resales len again
updated_resales_length = resales.shape[0]
print("Original length: ", original_resales_length)
print("Updated length: ", updated_resales_length)

# save to csv
resales.to_csv('../../data/cleaned_data/resales_processed.csv', index=False)

# PRINTS AFTER RUNNING - for records
# streets not in hdbpropertyinfo dataset:
# # {'ROCHOR RD', 'OUTRAM HILL', 'EAST COAST RD', 'SEMBAWANG RD', 'LIM CHU KANG RD'}
# No. of rows with no street name in hdbpropertyinfo dataset:  0
# No of blocks with no record in hdbpropertyinfo dataset:  4599
# Number of nan rows for max floor lvl:  0
# Original length:  905858
# Updated length:  905551

# no. of blocks with no record in hdbpropertyinfo dataset
# ANG MO KIO AVE 1 {'308', '307'}
# BEDOK STH AVE 3 {'46'}
# DEPOT RD {'103'}
# BOON LAY AVE {'219'}
# COMMONWEALTH DR {'57', '70', '71', '63', '73', '56', '69', '67', '55', '61', '68', '72', '60', '62'}
# TANGLIN HALT RD {'38', '42', '37', '32', '34', '35', '26', '27', '45', '28', '36', '25', '40', '43', '31', '30'}
# HOLLAND DR {'16', '17', '15'}
# TOA PAYOH CTRL {'79'}
# REDHILL CLOSE {'10', '15'}
# TIONG BAHRU RD {'1', '7', '5', '9', '3'}
# GHIM MOH RD {'11'}


# # do the same for rentals dataset
# rentals['max_floor_lvl'] = rentals.apply(lambda row: d[row['street_name']].get(row['block'], np.nan), axis=1)
# rentals = rentals[~rentals['max_floor_lvl'].isna()]
# # note: rentals dataset has no storey info

# #######################################
# # ADD DISTANCE TO NEAREST GREEN SPACE #
# #######################################

# # import parks.geojson
# import json
# from bs4 import BeautifulSoup

# with open('Parks.geojson') as f:
#     parksjson = json.load(f)

# def get_name(place):
#     description = place['properties']['Description']
#     soup = BeautifulSoup(description, 'html.parser')
#     name = soup.find('td').text.upper()
#     return name

# def get_coordinates(place):
#     return place['geometry']['coordinates'][:2]

# parks_and_pcns = pd.DataFrame(columns=['name', 'lng', 'lat'])  # create empty dataframe

# for park in parksjson['features']:
#     name = get_name(park)
#     lng, lat = get_coordinates(park)
#     # use pandas concat
#     to_add = pd.DataFrame({'name': [name], 'lng': [lng], 'lat': [lat]})
#     parks_and_pcns = pd.concat([parks_and_pcns, to_add], ignore_index=True)

# # get PCN access points
# with open('PCNAccessPoints.geojson') as f:
#     pcnjson = json.load(f)

# for pcn in pcnjson['features']:
#     name = get_name(pcn)
#     to_add = pd.DataFrame({'name': [name], 'lng': [lng], 'lat': [lat]})
#     parks_and_pcns = pd.concat([parks_and_pcns, to_add], ignore_index=True)

# from math import sin, cos, sqrt, atan2, radians
# from sklearn.neighbors import NearestNeighbors

# # earth distance function
# def earth_distance(x, y):
#   R = 6373.0

#   lat1, lng1 = radians(x[0]), radians(x[1])
#   lat2, lng2 = radians(y[0]), radians(y[1])

#   dlon = lng2 - lng1
#   dlat = lat2 - lat1

#   a = sin(dlat / 2)**2 + cos(lat1) * cos(lat2) * sin(dlon / 2)**2
#   c = 2 * atan2(sqrt(a), sqrt(1 - a))
#   return R * c

# # Create a KNeighborsClassifier model
# print("Fitting KNN model...")
# knn = NearestNeighbors(n_neighbors=1, algorithm='auto', metric=earth_distance)
# knn.fit(parks_and_pcns[['lat', 'lng']])

# # fit to resales dataset
# print("Fitting resales dataset...")
# distances, indices = knn.kneighbors(resales[['lat', 'lng']])
# resales['nearest_park_dist'] = distances
# resales['nearest_park'] = parks_and_pcns.iloc[indices.flatten()]['name'].values

# # fit to rentals dataset
# print("Fitting rentals dataset...")
# distances, indices = knn.kneighbors(rentals[['lat', 'lng']])
# rentals['nearest_park_dist'] = distances
# rentals['nearest_park'] = parks_and_pcns.iloc[indices.flatten()]['name'].values

# ###############
# # SAVE TO CSV #
# ###############

# print("Saving to CSV...")
# resales.to_csv('../../data/cleaned_data/resales_processed.csv', index=False)
# rentals.to_csv('../../data/cleaned_data/rentals_processed.csv', index=False)
