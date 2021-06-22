
# Load libraries
from flask import Flask, render_template, request
import geopy
from geopy.geocoders import Nominatim
import numpy as np
import pandas as pd
import pickle
from sklearn.preprocessing import LabelEncoder
from sklearn.preprocessing import StandardScaler
from tensorflow import keras


application = Flask(__name__ , template_folder='templates')

model = keras.models.load_model('model')

scaler = pickle.load(open('model/scaler.pkl', 'rb'))

encoder = pickle.load(open('model/encoder.pkl', 'rb'))

geolocator = Nominatim(user_agent="SD Flask App")

@application.route('/')
def index():

    return(render_template('index.html'))

@application.route('/result', methods=['POST', 'GET'])
def result():
    if request.method == 'GET':
        return('The URL /data is accessed directly. Try going to "/form" to submit form')
    if request.method == 'POST':
        form_data = request.form
        location = geolocator.geocode(' '.join([form_data['address'], form_data['city'], form_data['state'], form_data['zipcode']]))
        lat = location.latitude
        lon = location.longitude
        modelInput = scaler.transform(pd.DataFrame({'Latitude':[lat], 'Longitude': [lon]}))
        result = encoder.inverse_transform(np.argmax(model.predict(modelInput), axis=-1))[0]
        return(render_template('result.html', value = result))

if __name__ == '__main__':
    application.run(host='0.0.0.0', debug=True)
