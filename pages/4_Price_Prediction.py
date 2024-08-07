# load a linear regression model

import streamlit as st
import pandas as pd
import numpy as np

import sys
sys.path.append('utils')

from constants import town_choices, flat_type_choices, flat_model_choices, month_choices
from functions import generate_predictions, format_price

st.set_page_config(
    layout="wide",
)

st.header('Predicting resale and rental prices')


###################################
# GET USER INPUTS FOR EACH COLUMN #
###################################

# inputs have to correspond to the x_features of the model
# here, input features are: town, flat_type, floor_area_sqm,
# year_sold, average_storey, station_dist, mall_dist, hawker_dist, nearest_supermarket, nearest_amenity_disti, max_floor_level, nearest_park


with st.form("user_input"):

    main_col_1, main_col_2 = st.columns(2)

    with main_col_1:

        month_col, year_col = st.columns(2)

        with month_col:
            month_sold = st.selectbox('When do you want to buy/sell?', month_choices, index=2)

        with year_col:
            year_sold = st.number_input('', min_value=1990, max_value=2040, value=2024)

        town_col, remaining_lease_col = st.columns(2)

        with town_col:
            town = st.selectbox('Where is your resale flat located?', town_choices, index=5)

        with remaining_lease_col:
            remaining_lease = st.number_input('How old will the flat be?', min_value=1, max_value=99, value=20)

        flat_type_col, flat_model_col = st.columns(2)

        with flat_type_col:
            flat_type = st.selectbox('What is the flat type?', flat_type_choices, index=3)

        with flat_model_col:
            flat_model = st.selectbox('What is the flat model?', flat_model_choices, index=3)

        floor_area_sqm = st.slider('How big is the flat in square meters?', min_value=20, max_value=200, value=100, step=10)

        average_storey_col, max_floor_lvl_col = st.columns(2)

        with average_storey_col:
            average_storey = st.slider('On what floor is the flat located?', min_value=1, max_value=50, value=10)

        with max_floor_lvl_col:
            max_floor_lvl = st.slider('What is the maximum floor level?', min_value=1, max_value=50, value=10)

    with main_col_2:

        st.markdown('<strong>How close is the flat to...</strong> (in metres)', unsafe_allow_html=True)

        station_dist = st.slider('...an MRT station (in metres)', min_value=0, max_value=2000, value=500, step=50)

        mall_col, school_col = st.columns(2)
        hawker_col, supermarket_col = st.columns(2)
        # with park_col:
        #     nearest_park_dist = st.slider('...a park (in metres)', min_value=0, max_value=2000, value=500, step=50)

        with mall_col:
            nearest_mall_dist = st.slider('...a shopping mall', min_value=0, max_value=3000, value=500, step=100)

        with school_col:
            nearest_school_dist = st.slider('...a primary school', min_value=0, max_value=3000, value=500, step=100)

        with hawker_col:
            nearest_hawker_dist = st.slider('...a hawker centre', min_value=0, max_value=3000, value=500, step=100)

        with supermarket_col:
            nearest_supermarket_dist = st.slider('...a supermarket', min_value=0, max_value=3000, value=500, step=100)

        submitted = st.form_submit_button("Predict price")

if submitted:
    # code for prediction
    print('Predicting price...')
    predictions = generate_predictions(year_sold, month_sold, town, flat_type, flat_model, floor_area_sqm, average_storey, max_floor_lvl, station_dist, nearest_mall_dist, nearest_school_dist, nearest_hawker_dist, nearest_supermarket_dist, remaining_lease)

    # prediction rounded to nearest thousand
    resale_price = np.rint(round(predictions['resale_price'][0], -3))
    rental_price = np.rint(round(predictions['rental_price'][0], -1))

    # confidence interval rounded to two decimal places
    # confidence_interval = np.rint(prediction.conf_int())

    # lower = confidence_interval[0][0]
    # upper = confidence_interval[0][1]

    st.markdown(f'''
        <div style="display: flex; justify-content: space-around; align-items: center; padding: 20px; border: 1px solid rgba(49, 51, 63, 0.2); margin-top: 20px; border-radius: 0.5rem">
             <div style="text-align: center; width: 30%">
                <h3>For this <span style="color: rgb(255, 75, 75)">{flat_type.lower()}</span> flat in <br><span style="color: rgb(255, 75, 75)">{town}<span>...</h3>
             </div>
            <div style="text-align: center">
                 <h5>Predicted resale price</h5>
                 <h3>{format_price(resale_price)}</h3>
            </div>
            <div style="text-align: center">
                <h5>Predicted monthly rental</h5>
                <h3>{format_price(rental_price)}</h3>
            </div>


        </div>
                ''', unsafe_allow_html=True)
