# https://www.youtube.com/watch?v=iBeOvmt-tR0&ab_channel=MathisVanEetvelde
# https://towardsdatascience.com/deploy-neural-network-with-flask-docker-and-aws-beanstalk-6fd34373497a
# https://towardsdatascience.com/machine-learning-in-production-keras-flask-docker-and-heroku-933b5f885459
# https://towardsdatascience.com/deploying-deep-learning-models-using-tensorflow-serving-with-docker-and-flask-3b9a76ffbbda
# https://www.youtube.com/watch?v=zs3tyVgiBQQ&ab_channel=BeABetterDevBeABetterDev
# https://www.youtube.com/watch?v=GVs26OxzE3o&ab_channel=ParisNakitaKejserParisNakitaKejser
# https://gist.github.com/awssimplified/da49577fa48128e1da992dd6ec21085c
# https://www.youtube.com/watch?v=4oCjtzxWWJs&ab_channel=JustmeandOpensourceJustmeandOpensource
# https://docs.aws.amazon.com/elasticbeanstalk/latest/dg/docker.html


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
