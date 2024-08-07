# fuzzy-eureka

## Description

This repo contains code for the data preprocessing and visualisation of HDB resale and rentals data.

## Datasets used

* HDB rental dataset (https://beta.data.gov.sg/collections/166/view)
* HDB resale dataset (https://beta.data.gov.sg/collections/189/view)
* Primary schools from MOE website (https://www.moe.gov.sg/schoolfinder?journey=Primary%20school)
* Hawker centers from NEA (https://www.nea.gov.sg/docs/default-source/hawker-centres-documents/list-of-hcs_30-nov-2023.pdf)
* Supermarkets from SFA (https://beta.data.gov.sg/collections/1565/datasets/d_1bf762ee1d6d7fb61192cb442fb2f5b4/view)
* Train stations from LTA (https://www.lta.gov.sg/content/ltagov/en/map/train.html)
* Malls
* OneMap API for additional location data (mostly latitude and longitude) for HDB flats, train stations, primary schools, hawker centers, supermarkets and malls

## Data preprocessing

Most of the processed datasets have been removed from the repo because of their large size. The cleaned datasets are available at [date/cleaned_data](data/cleaned_data), with the resale sets having been split into five sets to keep under the 50mb limit. They have been imported and concatenated for Streamlit in [streamlit_app.py](streamlit_app.py).

But you can follow these commands to arrive at the cleaned dataset from the root folder:

```
python3 scripts/onemap_api_calls/first_call_main.py # warning, takes 3+ hours, calls onemap api for most of the location data
python3 scripts/onemap_api_calls/second_call_fix_errors.py # this fixes some wrong vals in the api calls
python3 scripts/data_processing/process_data.py # basic preprocessing
```

## Test notebook

There is a test notebook at [test_notebook.ipynb](test_notebook.ipynb). This is / can be used to test for any glaring errors, test out some visualisations etc.
