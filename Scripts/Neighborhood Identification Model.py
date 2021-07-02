
# --- Libraries --- #

# Load libraries
import pandas as pd
from pickle import dump
import os
from sklearn.preprocessing import LabelEncoder
from sklearn.preprocessing import StandardScaler
from tensorflow.keras import Sequential
from tensorflow.keras.layers import Dense


# --- Combine Neighborhood Data Files --- #

def LoadData(dataType):
    
    # Specifify input folder
    inputDirectory = 'data/Model Data - ' + dataType

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

# --- Data --- #

# Load data
neighborhoods = pd.read_csv('data/san diego neighborhoods.csv')

# Load data
trainData = LoadData('train')
testData = LoadData('test')


# --- Neural Network --- #

# Create train samples
trainSamples = trainData[['Latitude', 'Longitude']].to_numpy()
testSamples = testData[['Latitude', 'Longitude']].to_numpy()

# Create labels
trainLabels = trainData['Neighborhood']
testLabels = testData['Neighborhood']

# Create standard scaler
scaler = StandardScaler()

# Scale sample data
trainSamples = scaler.fit_transform(trainSamples)
testSamples = scaler.transform(testSamples)

# Create label encoder
encoder = LabelEncoder()

# Fit encoder to training labels
encoder.fit(trainLabels)

# Encode labels as integers
trainLabels = encoder.transform(trainLabels)
testLabels = encoder.transform(testLabels)

# Define the keras model
model = Sequential()
model.add(Dense(100, input_dim=2, activation='relu'))
model.add(Dense(200, activation='relu'))
model.add(Dense(len(set(trainLabels)), activation='softmax'))

# Compile model
model.compile(loss='sparse_categorical_crossentropy', optimizer='adam', metrics=['sparse_categorical_accuracy'])

# Run model
model.fit(trainSamples, trainLabels, epochs=300, batch_size=100)

# Evaluate model
model.evaluate(trainSamples, trainLabels)
model.evaluate(testSamples, testLabels)

# Save the model
model.save("model")

# Save the scalar
dump(scaler, open('model/assets/scaler.pkl', 'wb'))

# Save the encoder
dump(encoder, open('model/assets/encoder.pkl', 'wb'))
