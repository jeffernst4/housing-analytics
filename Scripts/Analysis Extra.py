
# Load libraries
import numpy as np
import pandas as pd
import pickle
import os
from sklearn.preprocessing import LabelEncoder
from sklearn.preprocessing import StandardScaler
from tensorflow.keras import Sequential
from tensorflow.keras.layers import Dense
from tensorflow import keras

# Load data
neighborhoods = pd.read_csv('Data/San Diego Neighborhoods.csv')


# --- Create Predictions --- #

def LoadData(dataDirectory):
    
    # Specifify input folder
    inputDirectory = 'Data/' + dataDirectory

    # List files in directory
    fileNames = os.listdir(inputDirectory)
    
    # Create empty list
    neighborhoodData = list()
    
    # Load all neighborhood data to a list
    for file in fileNames:
        
        # Load neighborhood data
        data = pd.read_csv(inputDirectory + '/' + file)
        
        # Create column of neighborhood name
        data['Neighborhood'] = os.path.splitext(file)[0]
        
        # Add data to data frame
        neighborhoodData.append(data)
    
    # Concatenate data frames
    neighborhoodData = pd.concat(neighborhoodData, axis=0, ignore_index=True)
    
    # Merge neighborhood district 
    neighborhoodData = pd.merge(neighborhoodData, neighborhoods[['District', 'Neighborhood']], how='left', on='Neighborhood')
    
    # Remove extra columns
    neighborhoodData = neighborhoodData[['MLS#', 'LATITUDE', 'LONGITUDE', 'District', 'Neighborhood']]
    
    # Rename columns
    neighborhoodData = neighborhoodData.rename(columns={'LATITUDE': 'Latitude', 'LONGITUDE': 'Longitude'})
    
    # Return data
    return(neighborhoodData)

housingData = LoadData('Redfin Housing Data/2 Bed Housing')

# Remove extra columns
housingData = housingData[['MLS#',
                           'SOLD DATE',
                           'PROPERTY TYPE',
                           'PRICE',
                           '$/SQUARE FEET',
                           'HOA/MONTH',
                           'BEDS',
                           'BATHS',
                           'SQUARE FEET',
                           'LOT SIZE',
                           'YEAR BUILT',
                           'ADDRESS',
                           'CITY',
                           'STATE OR PROVINCE',
                           'ZIP OR POSTAL CODE',
                           'LATITUDE',
                           'LONGITUDE']]

# Rename columns
housingData = housingData.rename(columns={'SOLD DATE':'Date Sold',
                                          'PROPERTY TYPE':'Property Type',
                                          'PRICE':'Price',
                                          '$/SQUARE FEET':'Price per Square Feet',
                                          'HOA/MONTH':'HOA per Month',
                                          'BEDS':'Beds',
                                          'BATHS':'Baths',
                                          'SQUARE FEET':'Square Feet',
                                          'LOT SIZE':'Lot Size',
                                          'YEAR BUILT':'Year Built',
                                          'ADDRESS':'Address',
                                          'CITY':'City',
                                          'STATE OR PROVINCE':'State',
                                          'ZIP OR POSTAL CODE':'Zip Code',
                                          'LATITUDE': 'Latitude',
                                          'LONGITUDE': 'Longitude'})



model = keras.models.load_model('Model')

scaler = pickle.load(open('Model/Scaler.pkl', 'rb'))

encoder = pickle.load(open('Model/Encoder.pkl', 'rb'))

lat = 33.024298
lon = -117.104827

modelInput = scaler.transform(pd.DataFrame({'Latitude':[lat], 'Longitude': [lon]}))

result = encoder.inverse_transform(np.argmax(model.predict(modelInput), axis=-1))[0]






# Create model input
modelInput = scaler.transform(housingData[['Latitude', 'Longitude']])

# Predict neighborhoods
housingData['Neighborhood'] = encoder.inverse_transform(np.argmax(model.predict(modelInput), axis=-1))

# Merge district
housingData = pd.merge(housingData, neighborhoods[['District', 'Neighborhood']], how='left', on='Neighborhood')

# Create variable for year sold
housingData['Year Sold'] = pd.DatetimeIndex(housingData['Date Sold'].astype('datetime64[ns]')).year




housingMetrics = pd.read_pickle('Data/Redfin Market Insights/Housing Metrics.pkl')
marketScores = pd.read_pickle('Output/Market Scores.pkl')

# Transformations

marketInsights['Metric_Value'] = marketInsights['Metric_Value'].str.replace(r'[^\.0-9]', '')

marketInsights = marketInsights[marketInsights['Metric_Value'] != '']

marketInsights['Metric_Value'] = marketInsights['Metric_Value'].astype(float)

marketInsights['Metric_Date'] = pd.to_datetime(marketInsights['Metric_Date'])

marketInsights['Metric_Year'] = marketInsights['Metric_Date'].dt.year

marketInsights['Metric_Date'] = marketInsights['Metric_Date'].dt.strftime('%Y-%m')



insightSummaryRecent = marketInsights[(marketInsights['Metric_Date'] >= '2018-07') & (marketInsights['Metric_Date'] < '2019-11')].groupby(['Neighborhood', 'Metric_Name'], as_index=False)['Metric_Value'].agg({'Metric_Value_Recent': 'median'})

insightSummaryPast = marketInsights[(marketInsights['Metric_Date'] >= '2017-02') & (marketInsights['Metric_Date'] < '2018-07')].groupby(['Neighborhood', 'Metric_Name'], as_index=False)['Metric_Value'].agg({'Metric_Value_Past': 'median'})

insightSummary = pd.merge(insightSummaryPast, insightSummaryRecent, how='outer', on=['Neighborhood', 'Metric_Name'])

insightSummary['Metric_Value_Rank_Change'] = insightSummary.groupby('Metric_Name')['Metric_Value_Recent'].rank() - insightSummary.groupby('Metric_Name')['Metric_Value_Past'].rank()

insightSummary.loc[insightSummary['Metric_Name'].isin(['Homes with Price Drops', 'Median Days on Market']), 'Metric_Value_Rank_Change'] = insightSummary['Metric_Value_Rank_Change'] * -1

insightSummary = insightSummary.pivot(index='Neighborhood', columns='Metric_Name', values='Metric_Value_Rank_Change')

marketScores = marketScores.pivot(index='Neighborhood', columns='Metric_Name', values='Metric_Value')

insightSummary = pd.merge(insightSummary, marketScores, how='outer', on='Neighborhood')

insightSummary.to_csv('Analysis/Market Insight Summary.csv')



