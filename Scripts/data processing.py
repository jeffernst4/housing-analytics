
# --- Libraries --- #

# Load libraries
import pandas as pd


# --- Crime --- #

# Load data
crime_stats = pd.read_pickle('data/crime data/crime stats.pkl')
crime_weights = pd.read_csv('data/crime data/crime weights.csv')
neighborhood_populations = pd.read_csv('data/crime data/neighborhood populations.csv')

# Remove forward slash in dates
crime_stats['Date'] = [date.replace(' /', '') for date in crime_stats['Date']]

# Convert date column to date
crime_stats['Date'] = pd.to_datetime(crime_stats['Date'])

# Create year column
crime_stats['Year'] = crime_stats['Date'].dt.year

# Convert date to only year and month
crime_stats['Date'] = crime_stats['Date'].dt.strftime('%Y-%m')

# Remove data before 2016
crime_stats = crime_stats[crime_stats['Year'] >= 2016].reset_index(drop=True)

# Remove all asterisks
crime_stats = crime_stats.replace({'[*]':''}, regex=True)

# Set crime count column to integer
crime_stats['Crime_Count'] = crime_stats['Crime_Count'].astype('int')

# Merge crime weights
crime_stats = pd.merge(crime_stats, crime_weights, how='inner', on='Crime')

# Calculate weighted crime count
crime_stats['Weighted_Crime_Count'] = crime_stats['Crime_Count'] * crime_stats['Crime_Weight']

# Calculate total weighted crime count by month
crime_stats_summary = crime_stats.groupby(['Neighborhood', 'Date', 'Year'], as_index=False)['Weighted_Crime_Count'].sum()

# Calculate average weighted crime count by year
crime_stats_summary = crime_stats_summary.groupby(['Neighborhood', 'Year'], as_index=False)['Weighted_Crime_Count'].mean()

# Merge neighborhood populations
crime_stats_summary = pd.merge(crime_stats_summary, neighborhood_populations, how='inner', on=['Neighborhood', 'Year'])

# Calculate weighted count per 1000 people
crime_stats_summary['Crime_Per_1000'] = 1000 * crime_stats_summary['Weighted_Crime_Count'] / crime_stats_summary['Population']

# Write data frame to csv
crime_stats_summary.to_csv('data/app data/crime summary.csv', index=False)
