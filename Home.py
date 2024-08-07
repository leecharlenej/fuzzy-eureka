import pandas as pd
import streamlit as st

st.set_page_config(
    page_title="IT5006 Project",
    page_icon="chart_with_upwards_trend",
)

# import resale dataset
# streamlit run resale_filters.py

path = "data/cleaned_data/resales_processed_"
resales_frames = [pd.read_csv(f"{path}{letter}") for letter in
                  ['aa', 'ab', 'ac', 'ad', 'ae', 'af', 'ag', 'ah', 'ai', 'aj']]

columns = resales_frames[0].columns
for df in resales_frames:
    df.columns = columns

resales = pd.concat(resales_frames, axis=0, ignore_index=True)

############################
# Import dataset
############################


st.write("# IT5006 - Project (Milestone 1)")

st.map(resales, latitude='lat', longitude='lng', zoom=10)

st.markdown(
    """
    Contributors: Seah Ee Wei, Hew Sock Fang, Huang Zichen, Lee Shu Ling Charlene

    This project considers **resale and rental prices for HDB flats in Singapore**, based on publicly available data from the Singapore government. These datasets have been enriched with location data, including distances to the nearest train stations, primary schools, and other amenities such as hawker centres, malls and supermarkets.

    The main aims are to explore and visualise pricing trends, and evaluate factors which impact resale price and/or monthly rents in Singapore.

    The app is divided into two main sections:

    1. **Dashboard**: This contains a visualisation of trends and features that we think are most interesting to the user. We have limited the dataset used in this visualisation to ten years for the HDB resale dataset (2014 to 2023) and three years of the rental dataset (2021 to 2023, which is the complete dataset available for rental prices), for more accurate analyses.

    2. **Data Explorer**: This section allows the user to explore the data in more detail based on their own filters. Some users may already know what they are looking for, or may spot a trend in the dashboard that they wish to investigate further. With the explorer pages, the user can obtain the relevant data and test their own hypotheses. For a complete experience, the explorer pages can filter through the entire dataset for resales, which spans 1990 to 2024, and rentals, which spans 2021 to 2023.

    ### Happy exploring!
"""
)
