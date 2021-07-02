
# Load libraries
import folium
import geopy
from geopy.geocoders import Nominatim
import matplotlib as mpl
from matplotlib import pyplot as plt
import numpy as np
import pandas as pd
import pickle
import seaborn as sns
import time
import streamlit as st
from tensorflow import keras


@st.cache(allow_output_mutation=True)
def load_ml_model():

    # Create empty dictionary
    model = dict()

    # Load model and assets
    model['model'] = keras.models.load_model('model')
    model['scaler'] = pickle.load(open('model/assets/scaler.pkl', 'rb'))
    model['encoder'] = pickle.load(open('model/assets/encoder.pkl', 'rb'))

    # Return model
    return(model)

@st.cache(allow_output_mutation=True)
def load_neighborhood_data():

    # Load neighborhoods
    neighborhoods = pd.read_pickle('data/neighborhood data.pkl')

    # Load neighborhood data
    neighborhood_data = pd.read_pickle('data/neighborhood data.pkl')

    # Return model
    return(neighborhoods, neighborhood_data)

@st.cache(allow_output_mutation=True)
def load_geolocator():

    # Create geolocator
    geolocator = Nominatim(user_agent="neighborhood-identification")

    # Return model
    return(geolocator)

def identify_neighborhood(location, model):
    
    # Convert coordinates to model input
    modelInput = model['scaler'].transform(pd.DataFrame({'Latitude':[location.latitude], 'Longitude': [location.longitude]}))

    # Predict neighborhood
    neighborhood_result = model['encoder'].inverse_transform(np.argmax(model['model'].predict(modelInput), axis=-1))[0]

    # Return neighborhood result
    return(neighborhood_result)

def create_neighborhood_map(location):

    # Create a base map
    neighborhood_map = folium.Map(
        location=[location.latitude, location.longitude],
        zoom_start=13,
        min_zoom=11,
        max_zoom=16,
        tiles='cartodb positron'
    )

    # Create a marker
    map_marker = folium.Marker(location=[location.latitude, location.longitude])
    
    # Add marker to map
    map_marker.add_to(neighborhood_map)

    # Return neighborhood map
    return(neighborhood_map)

def create_page_structure():

    # Load model
    model = load_ml_model()

    # Load neighborhood data
    neighborhoods, neighborhood_data = load_neighborhood_data()

    # Create empty inputs
    neighborhood_input, address_input = ["", ""]

    # Load geolocator
    geolocator = load_geolocator()

    # Title
    st.title("Analyze a Neighborhood")

    # Search type box
    search_type = st.radio("Select a Search Type", ("Enter an Address", "Choose a Neighborhood"))

    if search_type == "Enter an Address":

        address_input = st.text_input("Enter a San Diego Address")

        if address_input:

            location = geolocator.geocode(address_input)

            neighborhood_input = identify_neighborhood(location, model)

    else:

        neighborhood_input = st.selectbox("Select a San Diego Neighborhood", sorted([''] + list(set(neighborhoods['Neighborhood']))))

    if neighborhood_input:

        if address_input != "":

            st.header("**" + neighborhood_input + "**")
            st.write(location.address)
            st.markdown(create_neighborhood_map(location)._repr_html_(), unsafe_allow_html=True)

        st.markdown('<h2 style="text-align:center;">' + neighborhood_input + ' by the Numbers</h2>', unsafe_allow_html=True)


        # Create rows
        row_0 = st.beta_columns((1, 1, 1))
        row_1 = st.beta_columns((1, 1, 1))
        row_2 = st.beta_columns((1, 1))
        row_3 = st.beta_columns((1, 1))

        # Filter neighborhood data
        neighborhood_data = neighborhood_data[neighborhood_data['Neighborhood'] == neighborhood_input]

        # Filter individual datasets
        crime = neighborhood_data[neighborhood_data['Metric_Name'] == 'Crime']
        price_estimates = neighborhood_data[neighborhood_data['Metric_Name'] == 'Price Estimate']
        median_days_on_market = neighborhood_data[neighborhood_data['Metric_Name'] == 'Median Days on Market']
        sale_to_list_price = neighborhood_data[neighborhood_data['Metric_Name'] == 'Sale-to-List Price']
        neighborhood_scores = neighborhood_data[neighborhood_data['Metric_Name'].isin(['Walk Score', 'Compete Score', 'Transit Score'])][['Metric_Name', 'Metric_Value']].set_index('Metric_Name').to_dict()['Metric_Value']



        with row_0[0]:

            try:

                st.markdown('<h3 style="text-align:center;">Competition</h3>', unsafe_allow_html=True)
                st.markdown('<p style="text-align:center;">' + str(int(neighborhood_scores['Compete Score'])) + '%</p>', unsafe_allow_html=True)

            except:

                st.markdown('<p style="text-align:center;">N/A</p>', unsafe_allow_html=True)

        with row_0[1]:

            try:

                st.markdown('<h3 style="text-align:center;">Walkability</h3>', unsafe_allow_html=True)
                st.markdown('<p style="text-align:center;">' + str(int(neighborhood_scores['Walk Score'])) + '%</p>', unsafe_allow_html=True)

            except:

                st.markdown('<p style="text-align:center;">N/A</p>', unsafe_allow_html=True)

        with row_0[2]:

            try:

                st.markdown('<h3 style="text-align:center;">Transit</h3>', unsafe_allow_html=True)
                st.markdown('<p style="text-align:center;">' + str(int(neighborhood_scores['Transit Score'])) + '%</p>', unsafe_allow_html=True)

            except:

                st.markdown('<p style="text-align:center;">N/A</p>', unsafe_allow_html=True)

        with row_1[0]:

            try:

                st.markdown('<h3 style="text-align:center;">Safety</h3>', unsafe_allow_html=True)
                st.markdown('<p style="text-align:center;">' + str(int(crime[crime['Year'] == max(crime['Year'])]['Metric_Value'].values[0])) + '%</p>', unsafe_allow_html=True)

            except:

                st.markdown('<p style="text-align:center;">N/A</p>', unsafe_allow_html=True)

        with row_1[1]:

            try:

                st.markdown('<h3 style="text-align:center;">5-Year Price Growth</h3>', unsafe_allow_html=True)
                st.markdown('<p style="text-align:center;">' + str(int(100 * (price_estimates[price_estimates['Year'] == max(price_estimates['Year'])]['Metric_Value'].values[0] / price_estimates[price_estimates['Year'] == min(price_estimates['Year'])]['Metric_Value'].values[0] - 1))) + '%</p>', unsafe_allow_html=True)

            except:

                st.markdown('<p style="text-align:center;">N/A</p>', unsafe_allow_html=True)

        with row_2[0]:

            st.markdown('<h3 style="text-align:center;">Safety</h1>', unsafe_allow_html=True)

            if not crime.empty:
            
                fig, ax = plt.subplots()
                sns.barplot(data=crime, x='Year', y='Metric_Value', palette=mpl.cm.RdYlGn(crime['Metric_Value'] * 0.01))
                ax.set(ylim=(0, 100))
                st.pyplot(fig)

            else:

                st.markdown('<p style="text-align:center;">No data available</p>', unsafe_allow_html=True)


        with row_2[1]:

            st.markdown('<h3 style="text-align:center;">Housing Price Estimates</h3>', unsafe_allow_html=True)

            if not crime.empty:
            
                fig, ax = plt.subplots()
                sns.lineplot(data=price_estimates, x='Year', y='Metric_Value', color='#27AE60', marker='o', markersize=12, linewidth=3)
                ax.set(ylim=(0, price_estimates['Metric_Value'].max() * 1.10))
                st.pyplot(fig)

            else:

                st.markdown('<p style="text-align:center;">No data available</p>', unsafe_allow_html=True)

        with row_3[0]:

            st.markdown('<h3 style="text-align:center;">Median Days on Market</h3>', unsafe_allow_html=True)

            if not median_days_on_market.empty:

                fig, ax = plt.subplots()
                sns.lineplot(data=median_days_on_market, x='Year', y='Metric_Value', color='#D35400', marker='o', markersize=12, linewidth=3)
                ax.set(ylim=(0, median_days_on_market['Metric_Value'].max() * 1.10))
                st.pyplot(fig)
            else:
                st.markdown('<p style="text-align:center;">No data available</p>', unsafe_allow_html=True)

        with row_3[1]:

            st.markdown('<h3 style="text-align:center;">Sale-To-List Price</h3>', unsafe_allow_html=True)

            if not sale_to_list_price.empty:

                fig, ax = plt.subplots()
                sns.lineplot(data=sale_to_list_price, x='Year', y='Metric_Value', color='#D35400', marker='o', markersize=12, linewidth=3)
                ax.set(ylim=(95, 105))
                st.pyplot(fig)

            else:
                st.markdown('<p style="text-align:center;">No data available</p>', unsafe_allow_html=True)

