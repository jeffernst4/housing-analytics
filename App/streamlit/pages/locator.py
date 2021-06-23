
# Load libraries
import geopy
from geopy.geocoders import Nominatim
import numpy as np
import pandas as pd
import pickle
import streamlit as st
from tensorflow import keras

# Create geolocator
geolocator = Nominatim(user_agent="neighborhood-identification")

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

def identify_neighborhood(address_input, model):
    
    location = geolocator.geocode(address_input)
    lat = location.latitude
    lon = location.longitude
    modelInput = model['scaler'].transform(pd.DataFrame({'Latitude':[lat], 'Longitude': [lon]}))
    result = model['encoder'].inverse_transform(np.argmax(model['model'].predict(modelInput), axis=-1))[0]

    return(result)

def create_page_structure():

    model = load_ml_model()

    st.header('Find an Address')
        
    address_input = st.text_input('Enter a San Diego Address')

    if address_input:

        neighborhood = identify_neighborhood(address_input, model)

        st.write(neighborhood)


