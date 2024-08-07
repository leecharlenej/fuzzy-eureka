import pandas as pd

# read csv
resales = pd.read_csv('../../data/cleaned_data/resales_processed.csv')

# import rpi
rpi = pd.read_csv('rpi.csv')

# add quarter data for 2022 Q4: 171.9
# add quarter data for 2023 Q1, 2, 3, 4: 173.6, 176.2, 178.5, 180.4
# add quarter data for 2024 Q1: 183.5
# updates are from here: https://www.hdb.gov.sg/-/media/doc/EAPG-CSC/1Q2024-Flash-Estimate-RPI-Table.ashx

# make a dictionary of these values (to be converted into dataframe later)

rpi_dict = {
    '2022-10-01': 171.9,
    '2023-01-01': 173.6,
    '2023-04-01': 176.2,
    '2023-07-01': 178.5,
    '2023-10-01': 180.4,
    '2024-01-01': 183.5
}

# convert key to date NOT time
rpi_dict = {pd.to_datetime(k): v for k, v in rpi_dict.items()}

# make quarter column in rpi to datetime
rpi['quarter'] = pd.to_datetime(rpi['quarter'])

# convert rpi into dictionary quarter:index
original_rpi_dict = rpi.set_index('quarter')['index'].to_dict()

original_rpi_dict.update(rpi_dict)

# convert to dt.date
original_rpi_dict = {k.date(): v for k, v in original_rpi_dict.items()}

resales['month_sold'] = pd.to_datetime(resales['month_sold'])
resales['quarter'] = resales['month_sold'].dt.to_period('Q').dt.start_time.dt.date

resales['rpi'] = resales['quarter'].map(original_rpi_dict)

# save to csv
resales.to_csv('../../data/cleaned_data/resales_processed.csv', index=False)
