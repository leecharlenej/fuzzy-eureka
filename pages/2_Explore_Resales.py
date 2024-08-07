import streamlit as st
from streamlit_dynamic_filters import DynamicFilters
import plotly.express as px
import pandas as pd

# import resale dataset
# streamlit run resale_filters.py

path = "data/cleaned_data/resales_processed_"

resales1 = pd.read_csv(path + "aa")
resales2 = pd.read_csv(path + "ab")
resales3 = pd.read_csv(path + "ac")
resales4 = pd.read_csv(path + "ad")
resales5 = pd.read_csv(path + "ae")
resales6 = pd.read_csv(path + "af")
resales7 = pd.read_csv(path + "ag")
resales8 = pd.read_csv(path + "ah")
resales9 = pd.read_csv(path + "ai")
resales10 = pd.read_csv(path + "aj")

columns = resales1.columns
for df in [resales2, resales3, resales4, resales5, resales6, resales7, resales8, resales9, resales10]:
    df.columns = columns

############################
# Import dataset
############################

resales = pd.concat([resales1, resales2, resales3, resales4, resales5, resales6, resales7, resales8, resales9, resales10], axis=0, ignore_index=True)

############################
# Streamlit app starts here
############################
st.set_page_config(
    page_title="Resale Data",
    layout="wide",
    initial_sidebar_state="auto"
)

############################
# Sidebar
############################
with st.sidebar:
    st.subheader("Resale data: 1990 - 2024")
    resale_filters = DynamicFilters(resales, filters=['year_sold', 'town', 'flat_type'], filters_name="resalefilters")
    resale_filters.display_filters()

    with_price = st.slider("Price per sqm (SGD)", resales['price_per_sqm'].min(), resales['price_per_sqm'].max(), (resales['price_per_sqm'].min(), resales['price_per_sqm'].max()))
    resale_filter_price = resale_filters.filter_df()[(resale_filters.filter_df()['price_per_sqm'] >= with_price[0]) & (resale_filters.filter_df()['price_per_sqm'] <= with_price[1])]

    resale_filtered = resale_filter_price

############################
# Tabs
############################
tab1, tab2 = st.tabs(["Dashboard", "Data"])

############################
# Dashboard
############################
with tab1:
############################
# Row 0
############################
    # Row 0
    row_0 = col = st.columns((1), gap='Medium')
    with row_0[0]:
        st.subheader("Overview")
        with st.container(border=True):
            st.subheader("Summary")
            st.caption("*Distance to the nearest (km)")
            resale_filtered_summary = resale_filtered.describe()
            resale_filtered_summary1 = resale_filtered_summary.drop(["postal", "average_storey","lease_commence_date", "lat", "lng", "year_sold"], axis=1)
            resale_filtered_summary1.rename(columns={"year_sold": "Monthly Rent (SGD)",
                                                     "floor_area_sqm": "Floor Area (sqm)",
                                                     "remaining_lease": "Remaining Lease (years)",
                                                     "resale_price": "Resale Price (SGD)",
                                                     "price_per_sqm": "Price per sqm (SGD)",
                                                     "station_dist": "MRT Station*",
                                                     "nearest_mall_dist": "Mall*",
                                                     "nearest_hawker_dist": "Hawker Centre*",
                                                     "nearest_supermarket_dist": "Supermarket*",
                                                     "nearest_amenity_dist": "Amenities*",
                                                     "nearest_school_dist": "School*"}, inplace=True)
            st.dataframe(resale_filtered_summary1, use_container_width=True)

    st.divider()

############################
# Row 1 - No. of flats sold
############################
    st.subheader("No. of flats sold")
    row_1 = col = st.columns((1 ,1), gap='Medium')
    with row_1[0]:
        with st.container(border=True):
            st.subheader("No. of flats sold vs. Months")
            resale_filtered['month'] = pd.to_datetime(resale_filtered['month_sold']).dt.month_name()
            fig_countflat = px.histogram(resale_filtered, x="month", histfunc="count", color="flat_type")
            fig_countflat.update_layout(xaxis_title="Months", yaxis_title="No. of flats")
            st.plotly_chart(fig_countflat, use_container_width=True)

    with row_1[1]:
        with st.container(height = 550, border=True):
            st.subheader("No. of flats vs. Flat Types")
            fig_countflat = px.histogram(resale_filtered, x="flat_type", histfunc="count", category_orders={"flat_type": resale_filtered['flat_type'].sort_values().unique()})
            fig_countflat.update_layout(xaxis_title="Flat types", yaxis_title="No. of flats")
            st.plotly_chart(fig_countflat, use_container_width=True)

    st.divider()

############################
# Row 1
############################
    st.subheader("Prices")
    row_1 = col = st.columns((1,1,1,1), gap='Medium')
    with row_1[0]:
        st.info("Mean Resale Price per sqm")
        st.metric(label="Mean",value=f"SGD {resale_filtered['price_per_sqm'].mean():,.0f}")

    with row_1[1]:
        st.info("Median Resale Price per sqm")
        st.metric(label="Median",value=f"SGD {resale_filtered['price_per_sqm'].median():,.0f}")

    with row_1[2]:
        st.info("Min. Resale Price per sqm")
        st.metric(label="Minimum",value=f"SGD {resale_filtered['price_per_sqm'].min():,.0f}")

    with row_1[3]:
        st.info("Max. Resale Price per sqm")
        st.metric(label="Maximun",value=f"SGD {resale_filtered['price_per_sqm'].max():,.0f}")

############################
# Row 2
############################
    row_2 = col = st.columns((1), gap='Medium')
    with row_2[0]:
        with st.container(border=True):
            st.subheader("Average price per sqm vs. towns")
            fig_pricetowns = px.box(resale_filtered, x="town", y="price_per_sqm")
            fig_pricetowns.update_layout(xaxis_title="Town", yaxis_title="Price per sqm (SGD)")
            st.plotly_chart(fig_pricetowns, use_container_width=True)

    st.divider()

############################
# Row 3
############################
    st.subheader("Top 3 nearest")
    row_3 = col = st.columns((1,1,1), gap='Small')
    with row_3[0]:
        st.info("MRT Stations")
        top_3_nearest_stations = resale_filtered['nearest_station'].drop_duplicates().head(3)
        top_3_nearest_stations.reset_index(drop=True, inplace=True)
        st.dataframe(top_3_nearest_stations, use_container_width=True)
    with row_3[1]:
        st.info("Schools")
        top_3_nearest_schools = resale_filtered['nearest_school'].drop_duplicates().head(3)
        top_3_nearest_schools.reset_index(drop=True, inplace=True)
        st.dataframe(top_3_nearest_schools, use_container_width=True)
    with row_3[2]:
        st.info("Malls")
        top_3_nearest_malls = resale_filtered['nearest_mall'].drop_duplicates().head(3)
        top_3_nearest_malls.reset_index(drop=True, inplace=True)
        st.dataframe(top_3_nearest_malls, use_container_width=True)

############################
# Row 4
############################
    st.subheader("Nearest distance from amenities")
    row_4 = col = st.columns((1,1), gap='Medium')
    hover_columns = ['station_dist', 'nearest_station', 'price_per_sqm', 'flat_type']
    with row_4[0]:
        with st.container(border=True):
            st.subheader("Price per sqm vs. Nearest MRT Station Distance")
            fig_pricestat_scatter = px.scatter(resale_filtered, x="station_dist", y="price_per_sqm", color="flat_type", hover_data=hover_columns)
            fig_pricestat_scatter.update_layout(xaxis_title="Distance from amenity (km)", yaxis_title="Price per sqm (SGD)")
            st.plotly_chart(fig_pricestat_scatter, use_container_width=True)
    with row_4[1]:
        with st.container(border=True):
            st.subheader("Price per sqm vs. Nearest School Distance")
            fig_schooldist_scatter = px.scatter(resale_filtered, x="nearest_school_dist", y="price_per_sqm", color="flat_type")
            fig_schooldist_scatter.update_layout(xaxis_title="Distance from school (km)", yaxis_title="Price per sqm (SGD)")
            st.plotly_chart(fig_schooldist_scatter, use_container_width=True)

############################
# Row 5
############################
    row_5 = col = st.columns((1,1), gap='Medium')
    with row_5[0]:
        with st.container(border=True):
            st.subheader("Price per sqm vs. Nearest Mall Distance")
            fig_malldist_scatter = px.scatter(resale_filtered, x="station_dist", y="price_per_sqm", color="flat_type")
            fig_malldist_scatter.update_layout(xaxis_title="Distance from mall (km)", yaxis_title="Price per sqm (SGD)")
            st.plotly_chart(fig_malldist_scatter, use_container_width=True)
    with row_5[1]:
        with st.container(border=True):
            st.subheader("Price per sqm vs. Nearest Hawker Centre Distance")
            fig_hawkerdist_scatter = px.scatter(resale_filtered, x="nearest_school_dist", y="price_per_sqm", color="flat_type")
            fig_hawkerdist_scatter.update_layout(xaxis_title="Distance from hawker center (km)", yaxis_title="Price per sqm (SGD)")
            st.plotly_chart(fig_hawkerdist_scatter, use_container_width=True)

############################
# Dashboard
############################
with tab2:
    resale_filters.display_df()
    # @st.cache
    # def convert_df(df):
    #     return df.to_csv().encode('utf-8')

    # csv = convert_df(resales)

    # st.download_button(
    #     "Download complete dataset as CSV",
    #     csv,
    #     "browser_visits.csv",
    #     "text/csv",
    #     key='browser-data'
    # )

    #
