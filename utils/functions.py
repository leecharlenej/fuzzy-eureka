import pandas as pd
from models import resales_model, rentals_model
from constants import resale_town_mappings, flat_type_mappings, flat_model_mappings, month_mappings, rental_town_mappings

def generate_predictions(year_sold, month_sold, town, flat_type, flat_model, floor_area_sqm, average_storey, max_floor_lvl,
                        station_dist, nearest_mall_dist, nearest_school_dist, nearest_hawker_dist, nearest_supermarket_dist, remaining_lease):

    nearest_amenity_dist = min(nearest_mall_dist, nearest_hawker_dist, nearest_supermarket_dist)

    # create a dictionary of inputs
    resales_input_dict = {
        'month_sold': month_mappings[month_sold],
        'year_sold': year_sold,
        'floor_area_sqm': floor_area_sqm,
        'average_storey': average_storey,
        'remaining_lease': 99 - remaining_lease,
        'town': int(resale_town_mappings[town.upper()]),
        'flat_type': int(flat_type_mappings[flat_type.upper()]),
        'flat_model': int(flat_model_mappings[flat_model]),

        # 'nearest_mall_dist': nearest_mall_dist/1000,
        # 'nearest_park_dist': nearest_park_dist/1000,
        'nearest_school_dist': nearest_school_dist/1000,
        'station_dist': station_dist/1000,
        'nearest_amenity_dist': nearest_amenity_dist/1000,
        'max_floor_lvl': max_floor_lvl,
        # 'nearest_hawker_dist': nearest_hawker_dist/1000,
        # 'nearest_supermarket_dist': nearest_supermarket_dist/1000
    }

    rentals_input_dict = {
        'town': int(rental_town_mappings[town.upper()]),
        'year_approved': year_sold,
        'flat_type': int(flat_type_mappings[flat_type.upper()]),
        'max_floor_lvl': max_floor_lvl,
        'station_dist': station_dist/1000,
        'amenity_dist': nearest_amenity_dist/1000,
        'school_dist': nearest_school_dist/1000,
    }

    # create a dataframe from the dictionary
    resales_input_dict = pd.DataFrame(resales_input_dict, index=[0])
    # print(resales_input_dict)

    rentals_input_dict = pd.DataFrame(rentals_input_dict, index=[0])
    # print(rentals_input_dict)

    # make prediction
    resale_prediction = resales_model.predict(resales_input_dict)
    rental_prediction = rentals_model.predict(rentals_input_dict)

    return {'resale_price': resale_prediction, 'rental_price': rental_prediction}

def format_price(price):
    dollars = str(int(price))[::-1]
    new_string = ''

    while len(dollars) > 3:
        new_string += dollars[:3] + ','
        dollars = dollars[3:]
    new_string += dollars
    return '$' + new_string[::-1]

def format_price(price):
    dollars = str(int(price))[::-1]
    new_string = ''

    while len(dollars) > 3:
        new_string += dollars[:3] + ','
        dollars = dollars[3:]
    new_string += dollars
    return '$' + new_string[::-1]
