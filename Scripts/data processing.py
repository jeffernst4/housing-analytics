
# --- Libraries --- #

# Load libraries
from datetime import date
import os
import pandas as pd
import re


# --- ARJIS Crime --- #

def load_crime_data():
    
    # Specifify input folder
    input_directory = 'data/crime data/crime rates'

    # List files in directory
    file_names = os.listdir(input_directory)
    
    # Create empty list
    crime_stats = list()
    
    # Load all neighborhood data to a list
    for file in file_names:
        
        # Load neighborhood data
        data = pd.read_csv(input_directory + '/' + file)
        
        # Create column of neighborhood name
        data['Year'] = os.path.splitext(file)[0]
        
        # Add data to data frame
        crime_stats.append(data)
    
    # Concatenate data frames
    crime_stats = pd.concat(crime_stats, axis=0, ignore_index=True)
    
    # Return data
    return(crime_stats)

def summarize_crime(crime_stats, crime_weights, neighborhoods, neighborhood_populations):

    # Convert crime stats to a long version
    crime_stats = crime_stats.melt(id_vars=['Neighborhood', 'Year'], var_name='Crime', value_name='Crime_Rate')
    
    # Rename neighborhood column
    crime_stats = crime_stats.rename(columns={'Neighborhood':'Neighborhood_Name_ARJIS'})
    
    # Set year column to int
    crime_stats['Year'] = crime_stats['Year'].astype('int')
    
    # Set crime count column to string
    crime_stats['Crime_Rate'] = crime_stats['Crime_Rate'].astype('str')
    
    # Remove commas from crime rate
    crime_stats['Crime_Rate'] = crime_stats['Crime_Rate'].str.replace(',', '')
    
    # Set crime rate column to float
    crime_stats['Crime_Rate'] = crime_stats['Crime_Rate'].astype('float')
    
    # Merge crime weights
    crime_stats = pd.merge(crime_stats, crime_weights, how='inner', on='Crime')
    
    # Calculate weighted crime rate
    crime_stats['Weighted_Crime_Rate'] = crime_stats['Crime_Rate'] * crime_stats['Crime_Weight']
    
    # Calculate total weighted crime rate
    crime_summary = crime_stats.groupby(['Neighborhood_Name_ARJIS', 'Year'], as_index=False)['Weighted_Crime_Rate'].sum()
    
    # Merge neighborhoods
    crime_summary = pd.merge(crime_summary, neighborhoods[['Neighborhood', 'Neighborhood_Name_ARJIS']], how='inner', on='Neighborhood_Name_ARJIS')
    
    # Merge neighborhood populations
    crime_summary = pd.merge(crime_summary, neighborhood_populations, how='inner', on=['Neighborhood_Name_ARJIS', 'Year'])
    
    # Calculate population ratio
    crime_summary['Population_Ratio'] = crime_summary.groupby(['Neighborhood', 'Year'])['Weighted_Crime_Rate'].apply(lambda x: x / float(x.sum()))
    
    # Apply population ratio to weighted crime rate
    crime_summary['Weighted_Crime_Rate'] = crime_summary['Weighted_Crime_Rate'] * crime_summary['Population_Ratio']
    
    # Calculate total weighted crime count by neighborhood and year
    crime_summary = crime_summary.groupby(['Neighborhood', 'Year'], as_index=False)[['Weighted_Crime_Rate', 'Population']].sum()
    
    crime_summary['Weighted_Crime_Rate'] = crime_summary['Weighted_Crime_Rate']**(1/4)
    
    crime_summary['Weighted_Crime_Rate'] = crime_summary['Weighted_Crime_Rate'].max() - crime_summary['Weighted_Crime_Rate']
    
    crime_summary['Weighted_Crime_Rate'] = crime_summary['Weighted_Crime_Rate'] / (crime_summary['Weighted_Crime_Rate'].max() - crime_summary['Weighted_Crime_Rate'].min()) * 100
    
    # Add metric name column to crime stats summary
    crime_summary = pd.DataFrame({'Neighborhood':crime_summary['Neighborhood'], 'Year':crime_summary['Year'], 'Metric_Name':'Crime', 'Metric_Value':crime_summary['Weighted_Crime_Rate']})
    
    # Return crime summary
    return(crime_summary)


# --- Redfin Housing Metrics --- #

def summarize_housing_metrics(housing_metrics, neighborhoods):
    
    # Remove duplicates
    housing_metrics.drop_duplicates(inplace=True)
    
    # Convert date column to date
    housing_metrics['Date'] = pd.to_datetime(housing_metrics['Date'])
    
    # Create year column
    housing_metrics['Year'] = housing_metrics['Date'].dt.year
    
    # Remove characters that are not digits
    housing_metrics['Metric_Value'] = housing_metrics['Metric_Value'].str.replace(r'[^\.0-9]', '', regex=True)
    
    # Remove blank values
    housing_metrics = housing_metrics[housing_metrics['Metric_Value'] != ''].reset_index(drop=True)
    
    # Convert metric value to a float
    housing_metrics['Metric_Value'] = housing_metrics['Metric_Value'].astype('float')
    
    # Calculate the mean value for every neighborhood, year, and metric
    housing_metrics_summary = housing_metrics.groupby(['Neighborhood', 'Year', 'Metric_Name'], as_index=False)['Metric_Value'].mean()
    
    # Return housing metrics summary
    return(housing_metrics_summary)


# --- Redfin Neighborhood Scores --- #

def summarize_neighborhood_scores(neighborhood_scores, neighborhoods):
    
    neighborhood_scores = pd.read_pickle('data/redfin market insights/neighborhood scores.pkl')
    
    # Remove duplicates
    neighborhood_scores.drop_duplicates(inplace=True)
    
    # Create year column
    neighborhood_scores['Year'] = int(date.today().year)
    
    # Convert metric value to a float
    neighborhood_scores['Metric_Value'] = neighborhood_scores['Metric_Value'].astype('int')
    
    # Calculate the mean value for every neighborhood, year, and metric
    neighborhood_scores_summary = neighborhood_scores.groupby(['Neighborhood', 'Year', 'Metric_Name'], as_index=False)['Metric_Value'].mean()
    
    # Return housing metrics summary
    return(neighborhood_scores_summary)


# --- Zillow Price Estimates --- #

def summarize_price_estimates(price_estimates, neighborhoods):

    # Filter for san diego
    price_estimates = price_estimates[price_estimates['City'] == 'San Diego']
    
    # Remove unneeded columns
    price_estimates = price_estimates[['RegionName'] + [column_name for column_name in price_estimates.columns if re.search('\d{4}-\d{2}-\d{2}', column_name)]]
    
    # Rename columns
    price_estimates = price_estimates.rename(columns={'RegionName': 'Neighborhood_Name_Zillow'})
    
    # Merge neighborhoods
    price_estimates = pd.merge(price_estimates, neighborhoods[['Neighborhood', 'Neighborhood_Name_Zillow']], how='inner', on='Neighborhood_Name_Zillow')
    
    # Melt data frame
    price_estimates = price_estimates.melt(
        id_vars='Neighborhood',
        value_vars=[i for i in price_estimates.columns if re.search('\d{4}-\d{2}-\d{2}', i)],
        var_name='Date', 
        value_name='Metric_Value'
    )
    
    # Convert date column to date
    price_estimates['Date'] = pd.to_datetime(price_estimates['Date'])
    
    # Create year column
    price_estimates['Year'] = price_estimates['Date'].dt.year
    
    # Remove data before 2016
    price_estimates = price_estimates[price_estimates['Year'] >= 2016].reset_index(drop=True)
    
    # Add metric name column
    price_estimates['Metric_Name'] = 'Price Estimate'
    
    # Create summary by year and neighborhood
    price_estimates_summary = price_estimates.groupby(['Neighborhood', 'Year', 'Metric_Name'], as_index=False)['Metric_Value'].mean()
    
    # Return price estimates summary
    return(price_estimates_summary)


# --- Data Summary --- #

# Load data
crime_stats = load_crime_data()
crime_weights = pd.read_csv('data/crime data/crime weights.csv')
housing_metrics = pd.read_pickle('data/redfin market insights/housing metrics.pkl')
neighborhood_scores = pd.read_pickle('data/redfin market insights/neighborhood scores.pkl')
price_estimates = pd.read_csv('data/zillow housing data/3 bed price estimates.csv')
neighborhoods = pd.read_csv('data/san diego neighborhoods.csv')
neighborhood_populations = pd.read_csv('data/crime data/neighborhood populations.csv')

neighborhood_summary_data = list()

neighborhood_summary_data.append(summarize_crime(crime_stats, crime_weights, neighborhoods, neighborhood_populations))
neighborhood_summary_data.append(summarize_housing_metrics(housing_metrics, neighborhoods))
neighborhood_summary_data.append(summarize_price_estimates(price_estimates, neighborhoods))

neighborhood_summary_data = {
     'crime':summarize_crime(crime_stats, crime_weights, neighborhoods, neighborhood_populations),
     'housing_metrics':summarize_housing_metrics(housing_metrics, neighborhoods),
     'price_estimates':summarize_price_estimates(price_estimates, neighborhoods),
     'neighborhood_scores':summarize_neighborhood_scores(neighborhood_scores, neighborhoods)
}

# Concatenate data frames
neighborhood_summary_data = pd.concat(neighborhood_summary_data, axis=0, ignore_index=True)

# Save neighborhood summary to pickle
neighborhood_summary_data.to_pickle('app/streamlit/data/neighborhood data.pkl')

# Save neighborhoods to pickle
neighborhoods.to_pickle('app/streamlit/data/neighborhoods.pkl')
