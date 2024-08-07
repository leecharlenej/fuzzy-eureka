import streamlit as st
from streamlit_dynamic_filters import DynamicFilters
import plotly.express as px
import pandas as pd

############################
# Import dataset
############################
rentals = pd.read_csv("data/cleaned_data/rentals_processed.csv")

############################
# Streamlit app starts here
############################
st.set_page_config(
    page_title="Rental Data",
    layout="wide",
    initial_sidebar_state="auto"
)

############################
# CSS for graphs
############################
# st.markdown(
#     f"""
#     <style>
#     .stPlotlyChart {{
#      border-radius: 5px;
#      box-shadow: 0 4px 8px 0 rgba(0, 0, 0, 0.20), 0 6px 20px 0 rgba(0, 0, 0, 0.30);
#     }}
#     </style>
#     """, unsafe_allow_html=True
# )

############################
# Sidebar
############################
with st.sidebar:
    st.subheader("Rental data: 2021 - 2023")

    rental_filters = DynamicFilters(rentals, filters=['year_approved', 'town', 'flat_type'], filters_name="rentalfilters")
    rental_filters.display_filters()

    rental_select = rental_filters.filter_df()

    with_rent = st.slider("Montly Rent (SGD)", rentals['monthly_rent'].min(), rentals['monthly_rent'].max(), (rentals['monthly_rent'].min(), rentals['monthly_rent'].max()))
    rent_filter_month = rental_select[(rental_select['monthly_rent'] >= with_rent[0]) & (rental_select['monthly_rent'] <= with_rent[1])]

    # with_station = st.slider("Distance to nearest MRT Station", rentals['station_dist'].min(), rentals['station_dist'].max(), (rentals['station_dist'].min(), rentals['station_dist'].max()))
    # rent_filter_station = rent_filter_month[(rent_filter_month['station_dist'] >= with_station[0]) & (rent_filter_month['station_dist'] <= with_station[1])]

    # with_school = st.slider("Distance to nearest school", rentals['school_dist'].min(), rentals['school_dist'].max(), (rentals['school_dist'].min(), rentals['school_dist'].max()))
    # rent_filter_school = rent_filter_station[(rent_filter_station['school_dist'] >= with_school[0]) & (rent_filter_station['school_dist'] <= with_school[1])]

    rental_filtered = rent_filter_month

############################
# Tabs
############################

tab1, tab2 = st.tabs(["Dashboard", "Data"])

############################
# Dashboard
############################
with tab1:
############################
# Row 0 - Overview
############################
    st.subheader("Overview")
    row_0 = col = st.columns((1), gap='Medium')
    with row_0[0]:
        with st.container(height=550, border=True):
            st.subheader("Summary")
            st.caption("*Distance to the nearest (km)")
            rental_filtered_summary = rental_filtered.describe()
            rental_filtered_summary1 = rental_filtered_summary.drop(["lat", "lng","year_approved"], axis=1)
            rental_filtered_summary1.rename(columns={"monthly_rent": "Monthly Rent (SGD)",
                                                     "station_dist": "MRT Station*",
                                                     "mall_dist": "Mall*",
                                                     "hawker_dist": "Hawker Centre*",
                                                     "supermarket_dist": "Supermarket*",
                                                     "amenity_dist": "Amenities*",
                                                     "school_dist": "School*"}, inplace=True)
            st.dataframe(rental_filtered_summary1, use_container_width=True)

    st.divider()

############################
# Row 1 - No. of flats sold
############################
    st.subheader("No. of flats sold")
    row_1 = col = st.columns((1,1), gap='Medium')
    with row_1[0]:
        with st.container(border=True):
            st.subheader("No. of flats vs. Months")
            rental_filtered['month'] = pd.to_datetime(rental_filtered['rent_approval_date']).dt.month_name()
            fig_countflat = px.histogram(rental_filtered, x="month", histfunc="count", color="flat_type")
            fig_countflat.update_layout(xaxis_title="Months", yaxis_title="No. of flats")
            st.plotly_chart(fig_countflat, use_container_width=True)
    with row_1[1]:
        with st.container(height=550, border=True):
            st.subheader("No. of flats vs. Flat Types")
            fig_countflat = px.histogram(rental_filtered, x="flat_type", histfunc="count", category_orders={"flat_type": rental_filtered['flat_type'].sort_values().unique()})
            fig_countflat.update_layout(xaxis_title="Flat types", yaxis_title="No. of flats")
            st.plotly_chart(fig_countflat, use_container_width=True)


    st.divider()

############################
# Row 2 - Prices
############################
    st.subheader("Prices")
    row_2 = col = st.columns((1,1,1,1), gap='Medium')  
    with row_2[0]:
        st.info("Mean Rental Price")
        st.metric(label="Mean",value=f"SGD {rental_filtered['monthly_rent'].mean():,.0f}")
    with row_2[1]:
        st.info("Median Rental Price")
        st.metric(label="Median",value=f"SGD {rental_filtered['monthly_rent'].median():,.0f}")
    with row_2[2]:
        st.info("Min. Rental Price")
        st.metric(label="Minimum",value=f"SGD {rental_filtered['monthly_rent'].min():,.0f}")
    with row_2[3]:
        st.info("Max. Rental Price")
        st.metric(label="Maximum",value=f"SGD {rental_filtered['monthly_rent'].max():,.0f}")


############################
# Row 3 - Prices
############################   
    row_3 = col = st.columns((1), gap='Medium')
    with row_3[0]:
        with st.container(border=True):
            st.subheader("Average rental prices vs. towns")
            fig_renttowns = px.box(rental_filtered, x="town", y="monthly_rent")
            fig_renttowns.update_layout(xaxis_title="Town", yaxis_title="Monthly rent (SGD)")
            fig_renttowns.update_layout(margin=dict(pad=0, r=20, t=50, b=60, l=60))
            st.plotly_chart(fig_renttowns, use_container_width=True)

    st.divider()

############################
# Row 4 - Top 3 nearest
############################
    st.subheader("Top 3 nearest")
    row_4 = col = st.columns((1,1,1), gap='Small')
    with row_4[0]:
        st.info("MRT Stations")
        top_3_nearest_stations = rental_filtered['nearest_station'].drop_duplicates().head(3)
        top_3_nearest_stations.reset_index(drop=True, inplace=True)
        st.dataframe(top_3_nearest_stations, use_container_width=True)
    with row_4[1]:
        st.info("Schools")
        top_3_nearest_schools = rental_filtered['nearest_school'].drop_duplicates().head(3)
        top_3_nearest_schools.reset_index(drop=True, inplace=True)
        st.dataframe(top_3_nearest_schools, use_container_width=True)
    with row_4[2]:
        st.info("Malls")
        top_3_nearest_malls = rental_filtered['nearest_mall'].drop_duplicates().head(3)
        top_3_nearest_malls.reset_index(drop=True, inplace=True)
        st.dataframe(top_3_nearest_malls, use_container_width=True)

############################
# Row 5 - Distance from amenities
############################ 
    st.subheader("Nearest distance from amenities")
    row_5 = st.columns((1,1), gap='Medium')
    with row_5[0]:
        with st.container(border=True):
            st.subheader("Rental prices vs. Nearest MRT Distance")
            fig_stationdist_scatter = px.scatter(rental_filtered, x="station_dist", y="monthly_rent", color="flat_type")
            fig_stationdist_scatter.update_layout(xaxis_title="Distance from station (km)", yaxis_title="Monthly rent (SGD)")
            fig_stationdist_scatter.update_layout(margin=dict(pad=0, r=20, t=50, b=60, l=60))
            st.plotly_chart(fig_stationdist_scatter, use_container_width=True)
    with row_5[1]:
        with st.container(border=True):
            st.subheader("Rental prices vs. Nearest School Distance")
            fig_schooldist_scatter = px.scatter(rental_filtered, x="school_dist", y="monthly_rent", color="flat_type")
            fig_schooldist_scatter.update_layout(xaxis_title="Distance from school (km)", yaxis_title="Monthly rent (SGD)")
            fig_schooldist_scatter.update_layout(margin=dict(pad=0, r=20, t=50, b=60, l=60))
            st.plotly_chart(fig_schooldist_scatter, use_container_width=True)
    
############################
# Row 6
############################
    row_6 = st.columns((1,1), gap='Medium')
    with row_6[0]:
        with st.container(border=True):
            st.subheader("Rental prices vs. Nearest Mall Distance")
            fig_malldist_scatter = px.scatter(rental_filtered, x="mall_dist", y="monthly_rent", color="flat_type")
            fig_malldist_scatter.update_layout(xaxis_title="Distance from mall (km)", yaxis_title="Monthly rent (SGD)")
            fig_malldist_scatter.update_layout(margin=dict(pad=0, r=20, t=50, b=60, l=60))
            st.plotly_chart(fig_malldist_scatter, use_container_width=True)
    with row_6[1]:
        with st.container(border=True):
            st.subheader("Rental prices vs. Nearest Hawker Centre Distance")
            fig_hawkerdist_scatter = px.scatter(rental_filtered, x="hawker_dist", y="monthly_rent", color="flat_type")
            fig_hawkerdist_scatter.update_layout(xaxis_title="Distance from hawker centre (km)", yaxis_title="Monthly rent (SGD)")
            fig_hawkerdist_scatter.update_layout(margin=dict(pad=0, r=20, t=50, b=60, l=60))
            st.plotly_chart(fig_hawkerdist_scatter, use_container_width=True)

############################
# Dashboard
############################
with tab2:
    rental_filters.display_df()