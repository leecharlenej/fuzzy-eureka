import pandas as pd
import streamlit as st
import matplotlib.pyplot as plt
import plotly.express as px
import plotly.graph_objects as go
from urllib.request import urlopen
import json
from copy import deepcopy
from plotly.subplots import make_subplots
import altair as alt
import seaborn as sns
import os

######################
# IMPORTING DATASETS #
######################

path = "data/cleaned_data/resales_processed_"
resales_frames = [pd.read_csv(f"{path}{letter}") for letter in
                  ['aa', 'ab', 'ac', 'ad', 'ae', 'af', 'ag', 'ah', 'ai', 'aj']]

columns = resales_frames[0].columns
for df in resales_frames:
    df.columns = columns

resales = pd.concat(resales_frames, axis=0, ignore_index=True)

# only resales in between 2004 to 2023
resales = resales[(resales['year_sold'] >= 2014) & (resales['year_sold'] <= 2023)]

resales['storey_bin'] = pd.cut(resales['average_storey'], bins=[0, 5, 10, 20, 100],
                               labels=['1-5', '6-10', '11-20', '20+'])

# rentals dataset
rentals = pd.read_csv('data/cleaned_data/rentals_processed.csv')

# geojson files and datasets for chloropleth map
geojson_path = 'layer.json'

with open(geojson_path) as response:
    geo = json.load(response)

# just resales for the last ten years
median_price_per_sqm = resales.groupby('town')['price_per_sqm'].median().reset_index()
median_price_per_sqm.rename(columns={'price_per_sqm': 'median_price_per_sqm'}, inplace=True)

# iterate through the geojson features and add the median price per sqm based on the town name
for feature in geo['features']:
    town_name = feature['properties']['Description']
    try:
        median_price = median_price_per_sqm[median_price_per_sqm['town'] == town_name]['median_price_per_sqm'].values[0]
    except IndexError:
        median_price = 0
        # add a row to the median_price_per_sqm dataframe
        to_add = pd.DataFrame({'town': [town_name], 'median_price_per_sqm': [median_price]})
        median_price_per_sqm = pd.concat([median_price_per_sqm, to_add], axis=0, ignore_index=True)
    feature['properties']['median_price_per_sqm'] = median_price


################
# PAGE CONFIGS #
################

# set wide layout
st.set_page_config(
    page_title="HDB Resale and Rental Prices",
    layout="wide",
    initial_sidebar_state="collapsed"
)

st.markdown(
    """
<style>
[data-testid="stMetricValue"] {
    font-size: 24px;
    margin: 0px;
#price-trends-over-the-last-ten-years {
    text-align: center;
}
[data]
</style>
""",
    unsafe_allow_html=True,
)

###########
# HEADERS #
###########

st.header("HDB resales in the last 10 years", divider='blue')

######################
# FIRST ROW OF PLOTS #
######################

######################
# TRANSACTION VOLUME #
######################

col0, col1, col2 = st.columns([4, 4, 3])

with col0:
    st.subheader('More flats are being sold')

    aggregated_data = resales.groupby(['year_sold', 'flat_type']).size().reset_index(name='counts')

    # Create the stacked bar plot
    fig = px.bar(aggregated_data,
                 x='year_sold',
                 y='counts',
                 color='flat_type',  # This specifies the stack by column
                 labels={'counts': 'Number of Resales', 'year_sold': 'Year Sold', 'flat_type': 'Flat Type'})

    fig.update_layout(width=400, height=550)
    fig.update_xaxes(title_text='Year Sold')
    fig.update_yaxes(title_text='Number of Resales')
    # overlay legend on plot
    fig.update_layout(legend=dict(
        orientation="h",
        yanchor="bottom",
        y=1.02,
        xanchor="right",
        x=1
    ))
    st.plotly_chart(fig)

#################################
# MEDIAN RESALE PRICE OVER TIME #
#################################

with col1:
    st.subheader('Resale prices have risen')
    # plot median resale price per sqm vs year sold

    median_resale_prices = resales.groupby('month_sold')['price_per_sqm'].median().reset_index()
    transaction_volume_by_month = resales.groupby('month_sold')['resale_price'].count().reset_index()
    fig = px.line(median_resale_prices, x='month_sold', y='price_per_sqm')
    # set y lim
    fig.update_yaxes(range=[3000, 7000])
    # set x label
    fig.update_xaxes(title_text='Year Sold')
    # set y label
    fig.update_yaxes(title_text='Median Resale Price per Sqm')
    # update size
    fig.update_layout(width=400, height=550)
    fig.add_annotation(
        text="Increase in median resale prices during the COVID period.",
        align='left',
        showarrow=False,
        xref='paper',
        yref='paper',
        x=0.5,
        y=0.05,
        font={'size': 14},
    )
    # display the plot
    st.plotly_chart(fig)

###################
# TOP THREE TOWNS #
###################

with col2:
    st.subheader('Top three towns')
    col3, col4 = st.columns(2)
    with col3:
        st.write("By transactions")
        st.metric('17,727 transactions', 'Sengkang')
        st.metric('15,779 transactions', 'Woodlands')
        st.metric('15,363 transactions', 'Jurong West')
    with col4:
        st.write('By price per sqm')
        st.metric('$7,458 psm', 'Central Area')
        st.metric('$6,880 psm', 'Queenstown')
        st.metric('$6,515 psm', 'Bukit Timah')
    # New row for additional metrics
    extra_metrics_container = st.container(border=True)
    with extra_metrics_container:
        # Additional metrics for transaction volume and growth rate
        st.write('Avg % increase in median psm (baseline 2014)')
        col1, col2 = st.columns(2)
        with col1:
            st.metric(label="a", value="Pre-COVID", delta='-11.3%', label_visibility="collapsed")
        with col2:
            st.metric(label="a", value='Post-COVID', delta='22.2%', label_visibility="collapsed")

        st.write('Avg % increase in transactions (baseline 2014)')
        col1, col2 = st.columns(2)
        with col1:
            st.metric(label="a", value='Pre-COVID', delta='44%', label_visibility="collapsed")
        with col2:
            st.metric(label="a", value='Post-COVID', delta='74.8%', label_visibility="collapsed")

#######################
# SECOND ROW OF PLOTS #
#######################

leftcol, rightcol = st.columns(2)

############
# MAP PLOT #
############

with leftcol:
    st.subheader('Central areas tend to command higher prices')

    # Create the chloropleth map using Graph Objects
    fig = go.Figure(go.Choropleth(
        geojson=geo,
        locations=median_price_per_sqm['town'],  # Make sure this matches your DataFrame
        z=median_price_per_sqm['median_price_per_sqm'],  # Data to be used for coloring
        featureidkey="properties.Description",  # Make sure this matches the identifier in your GeoJSON
        colorscale="sunset",  # Color scale
        marker_line_width=1,  # Border line width
        marker_line_color='black',  # Border color
    ))

    # Update map layout to fit chloropleth bounds and adjust visibility
    fig.update_layout(
        geo=dict(
            fitbounds="locations",
            visible=False,
        ),
        margin={"r": 0, "t": 0, "l": 0, "b": 0}  # Adjust margins to ensure the map uses the full space
    )

    # Add a note to the map
    fig.add_annotation(
        text="Average price per square meter of resale flats in each town.",
        align='left',
        showarrow=False,
        xref='paper',
        yref='paper',
        x=0.5,
        y=0.05,
        font={'size': 14},
    )
    fig.add_annotation(
        text="(Pale yellow values represent areas with no HDBs sold in the last 10 years.)",
        align='left',
        showarrow=False,
        xref='paper',
        yref='paper',
        x=0.5,
        y=0,
        font={'size': 14},
    )

    fig.update_layout(width=600)
    # Display the map in a Streamlit app
    st.plotly_chart(fig)

#######################
# STOREY BIN BOX PLOT #
#######################

with rightcol:
    st.subheader("So do flats on a higher storey")

    category_order = ['1-5', '6-10', '11-20', '20+']

    # box plot for storey_bin and price_per_sqm using plotly
    fig = px.box(resales, x='storey_bin', y='price_per_sqm', category_orders={'storey_bin': category_order})

    fig.update_layout(width=600)
    # update x label
    fig.update_xaxes(title_text='Floor level')
    # update y label
    fig.update_yaxes(title_text='Price per Sqm')
    st.plotly_chart(fig)

###################################
# DISTANCE TO NEAREST STUFF PLOTS #
###################################

st.subheader('Weak correlations between price and distance to transport, schools and amenities')

transportcol, schoolcol, amenitycol = st.columns(3)

with transportcol:
    # scatter chart for station_dist and price_per_sqm using plotly
    fig = px.scatter(resales, x='station_dist', y='price_per_sqm', color='town')
    fig.update_layout(width=400)
    fig.update_layout(height=300)
    # update x label
    fig.update_xaxes(title_text='Distance to nearest MRT (Correlation = -0.22)')
    # update y label
    fig.update_yaxes(title_text='Price per Sqm')
    # set height

    st.plotly_chart(fig)

with schoolcol:
    # scatter chart for nearest_school_dist and price_per_sqm using plotly
    fig = px.scatter(resales, x='nearest_school_dist', y='price_per_sqm', color='town')
    fig.update_layout(width=400)
    fig.update_layout(height=300)
    # update x label
    fig.update_xaxes(title_text='Distance to nearest primary school (Correlation = 0.12)')
    # update y label
    fig.update_yaxes(title_text='Price per Sqm')
    st.plotly_chart(fig)

with amenitycol:
    # scatter chart for nearest amenity distance and price_per_sqm using plotly
    fig = px.scatter(resales, x='nearest_amenity_dist', y='price_per_sqm', color='town')
    fig.update_layout(width=400)
    fig.update_layout(height=300)
    # update x label
    fig.update_xaxes(title_text='Distance to nearest amenity (Correlation = -0.19)')
    # update y label
    fig.update_yaxes(title_text='Price per Sqm')
    st.plotly_chart(fig)

##########################
# SAME THING FOR RENTALS #
##########################

st.header("HDB rentals in the last 3 years", divider='blue')

rentalscol0, rentalscol1, rentalscol3 = st.columns([3, 3, 2])

with rentalscol0:
    st.subheader('Rental volume dipped in 2022')

    # Create the stacked bar plot
    fig = px.bar(rentals, x='rent_approval_date', color='flat_type',
                 labels={'rent_approval_date': 'Rental Month', 'flat_type': 'Flat Type'})
    fig.update_layout(width=400)
    fig.update_xaxes(title_text='Month Rented')
    fig.update_yaxes(title_text='Number of Rentals')
    # overlay legend on plot
    fig.update_layout(legend=dict(
        orientation="h",
        yanchor="bottom",
        y=1.02,
        xanchor="right",
        x=1
    ))
    st.plotly_chart(fig)

with rentalscol1:
    st.subheader('Rental prices have risen')

    # line chart for median rental prices over time
    median_rental_prices = rentals.groupby('rent_approval_date')['monthly_rent'].median().reset_index()
    fig = px.line(median_rental_prices, x='rent_approval_date', y='monthly_rent')
    fig.update_layout(width=400)
    fig.update_xaxes(title_text='Year Approved')
    fig.update_yaxes(title_text='Median Monthly Rent (SGD)')
    st.plotly_chart(fig)

###################
# TOP THREE TOWNS #
###################

with rentalscol3:
    st.subheader('Top three towns')
    col3, col4 = st.columns(2)
    with col3:
        st.write("By no. of rentals")
        st.metric('7,607 rentals', 'Jurong West')
        st.metric('7.829 rentals', 'Tampines')
        st.metric('7,061 rentals', 'Sengkang')
    with col4:
        st.write('By monthly rental')
        st.metric('$2,800/month', 'Central Area')
        st.metric('$2,750/month', 'Bukit Merah')
        st.metric('$2,750/month', 'Bukit Timah')

    # New row for additional metrics
    extra_metrics_container = st.container()
    with extra_metrics_container:
        # Additional metrics for transaction volume and growth rate
        st.subheader('Rental volume & price')
        col1, col2 = st.columns(2)
        with col1:
            st.metric(label="% change in volume in", value='2022', delta='-13.7%')
        with col2:
            st.metric(label="% change in volume in", value='2023', delta='9.5%')
        col3, col4 = st.columns(2)
        with col3:
            st.metric(label="% change in rent in", value='2022', delta='17.5%')
        with col4:
            st.metric(label="% change in rent in", value='2023', delta='28.1%')


###################################
# DISTANCE TO NEAREST STUFF PLOTS #
###################################

st.subheader('Weak correlations between monthly rent and distance to transport, schools and amenities')

transportcolr, schoolcolr, amenitycolr = st.columns(3)

with transportcolr:
    # scatter chart for station_dist and monthly_rent using plotly
    fig = px.scatter(rentals, x='station_dist', y='monthly_rent', color='town',
                     labels={'station_dist': 'Distance to nearest MRT (km)', 'monthly_rent': 'Monthly Rent (SGD)'})
    fig.update_layout(width=400, height=300)
    fig.update_xaxes(title_text='Distance to nearest MRT (Correlation = -0.068)')
    fig.update_yaxes(title_text='Monthly Rent (SGD)')
    st.plotly_chart(fig)

with schoolcolr:
    # scatter chart for nearest_school_dist and monthly_rent using plotly
    fig = px.scatter(rentals, x='school_dist', y='monthly_rent', color='town',
                     labels={'school_dist': 'Distance to nearest primary school (km)',
                             'monthly_rent': 'Monthly Rent (SGD)'})
    fig.update_layout(width=400, height=300)
    fig.update_xaxes(title_text='Distance to nearest primary school (Correlation = -0.0006)')
    fig.update_yaxes(title_text='Monthly Rent (SGD)')
    st.plotly_chart(fig)

with amenitycolr:
    # scatter chart for nearest amenity distance and monthly_rent using plotly
    fig = px.scatter(rentals, x='amenity_dist', y='monthly_rent', color='town',
                     labels={'amenity_dist': 'Distance to nearest amenity (km)',
                             'monthly_rent': 'Monthly Rent (SGD)'})
    fig.update_layout(width=400, height=300)
    fig.update_xaxes(title_text='Distance to nearest amenity (Correlation = -0.008)')
    fig.update_yaxes(title_text='Monthly Rent (SGD)')
    st.plotly_chart(fig)

leftcolr, rightcolr = st.columns(2)

with leftcolr:
    st.subheader('Rental prices are higher in central areas')

    avg_rent_by_town_year = rentals.groupby(['town', 'year_approved'])['monthly_rent'].mean().reset_index()
    rentals_2023 = avg_rent_by_town_year[avg_rent_by_town_year['year_approved'] == 2023]

    # Calculate average rent for 2023 and sort
    sorted_towns_2023 = rentals_2023.sort_values(by='monthly_rent', ascending=False)['town'].tolist()

    # Plotting with px.density_heatmap
    fig = px.density_heatmap(avg_rent_by_town_year, x='year_approved', y='town', z='monthly_rent',
                             histfunc="avg", color_continuous_scale="Viridis",
                             category_orders={'town': sorted_towns_2023})
    fig.update_layout(width=600, height=400)
    # limit x axis to years
    fig.update_xaxes(title_text='Year Approved', tickmode='array', tickvals=[2021, 2022, 2023], type='category')
    fig.update_yaxes(title_text='Town')
    # update legend title
    fig.update_layout(coloraxis_colorbar=dict(title='Monthly Rent (SGD)'))
    st.plotly_chart(fig)

with rightcolr:

    st.subheader('Rental prices across flat types')
    # Calculate the average monthly rent per year
    category_order = ['1-ROOM', '2-ROOM', '3-ROOM', '4-ROOM', '5-ROOM', 'EXECUTIVE']
    fig = px.box(rentals, x='flat_type', y='monthly_rent',
                 labels={'flat_type': 'Flat Type', 'monthly_rent': 'Monthly Rent (SGD)'},
                 category_orders={'flat_type': category_order})
    fig.update_layout(width=600, height=400)
    st.plotly_chart(fig)
