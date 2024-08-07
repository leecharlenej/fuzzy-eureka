import pandas as pd
import numpy as np

############################
# IMPORTING RESALE DATASET #
############################

# import the dataset post-api calls

original_resale_data = pd.read_csv('../onemap_api_calls/resales_after_api_final.csv')

# copy into a new dataframe to avoid modifying the original
resales = original_resale_data.copy()

#############################
# PROCESSING RESALE DATASET #
#############################

# convert month to datetime object
resales['month'] = pd.to_datetime(resales['month'])

# rename month to month_sold
resales.rename(columns={'month': 'month_sold'}, inplace=True)

# add "year_sold" column, derived from "month_sold"
resales['year_sold'] = resales['month_sold'].dt.year

# add "remaining_lease" column, derived from "lease_commence_date" and "year_sold"
resales['remaining_lease'] = 99 - (resales['year_sold'] - resales['lease_commence_date'])

# drop rows where remaining_lease is more than 99 years (likely to be compute errors, and v small number of rows - unlikely to affect analysis)
resales = resales[resales['remaining_lease'] <= 99]

# add price per square meter based on resale_price divided by floor_area_sqm, rounded to the nearest whole number
resales['price_per_sqm'] = (resales['resale_price'] / resales['floor_area_sqm']).round(0)

# combine "MULTI-GENERATION" and "MULTI GENERATION" into "MULTI-GENERATION" for flat_type
resales['flat_type'] = resales['flat_type'].replace('MULTI GENERATION', 'MULTI-GENERATION')

# format the flat_model column consistently
resales['flat_model'] = resales['flat_model'].str.title()

# for storey_range, modify to get the upper and lower end of the range as integers
resales['storey_range'] = resales['storey_range'].str.split(' TO ')
resales['storey_range'] = resales['storey_range'].apply(lambda x: [int(i) for i in x])
resales['average_storey'] = resales['storey_range'].apply(lambda x: round((x[0] + x[1]) / 2))

# fixing missing postal codes manually
# only for three addresses: '11 GHIM MOH RD', '215 CHOA CHU KANG CTRL', '216 CHOA CHU KANG CTRL']
to_fix = resales[resales['postal'] == 'NIL']
to_fix['blk + street_name'] = to_fix['block'] + " " + to_fix['street_name']
# new postal codes, manually compiled from maps.google.com
new_postal_codes = {
    '11 GHIM MOH RD': '270011',
    '215 CHOA CHU KANG CTRL': '680215',
    '216 CHOA CHU KANG CTRL': '680216',
}
# put in new_postal_codes into to_fix
for blk_street, postal in new_postal_codes.items():
    to_fix.loc[to_fix['blk + street_name'] == blk_street, 'postal'] = postal
# drop blk + street_name column
to_fix = to_fix.drop(columns=['blk + street_name'])
# substitute to_fix back into resales
resales = resales[resales['postal'] != 'NIL']
resales = pd.concat([resales, to_fix], axis=0, ignore_index=True)

# fix all postal codes to be 6 digits
resales['postal'] = resales['postal'].apply(lambda x: str(x).zfill(6))

# reorder for better readability
resales = resales[['month_sold', 'year_sold', 'town', 'block', 'street_name', 'building', 'address', 'postal', 'flat_type', 'flat_model', 'storey_range', 'average_storey', 'floor_area_sqm', 'lease_commence_date', 'remaining_lease', 'resale_price', 'price_per_sqm', 'lat', 'lng', 'nearest_station', 'station_dist']]

#########################
# SAVING RESALE DATASET #
#########################

# save into new csv
resales.to_csv('../../data/cleaned_data/resales_processed.csv', index=False)


############################
# IMPORTING RENTAL DATASET #
############################

original_rental_data = pd.read_csv('../../data/original_rental_data/rental.csv')
rentals = original_rental_data.copy()

#############################
# PROCESSING RENTAL DATASET #
#############################

# convert rent_approval_date to datetime object
rentals['rent_approval_date'] = pd.to_datetime(rentals['rent_approval_date'])

# add year_approved column, derived from rent_approval_date
rentals['year_approved'] = rentals['rent_approval_date'].dt.year

# note: I considered if we could add location data to the rental datasets. but the block + town is insufficient to match it to a possible postal code. for example, bukit merah block 8 has different postal codes from the resale dataset. so we will not be adding location data to the rental dataset.

#########################
# SAVING RENTAL DATASET #
#########################

# save into new csv
rentals.to_csv('../../data/cleaned_data/rentals_processed.csv', index=False)
