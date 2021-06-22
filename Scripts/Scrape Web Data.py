
# --- Libraries --- #

# Load libraries
import os
import pandas as pd
from numpy import random
from selenium import webdriver
from selenium.webdriver import ActionChains
from selenium.webdriver.chrome.options import Options
import shutil
from time import sleep


# --- Functions --- #

class Pause:
    
    def Small():
        sleep(random.uniform(0.7, 1.3))
        
    def Medium():
        sleep(random.uniform(1.7, 2.3))
        
    def Large():
        sleep(random.uniform(2.7, 3.3))

def InitiateDriver(downloadDirectory=''):
    
    # Create chrome options
    chrome_options = Options()
    chrome_options.add_argument('--window-size=1920,1080')
    chrome_options.add_experimental_option('prefs', {'download.default_directory' : r'C:\Users\Jeff\Documents\Housing Analytics' + downloadDirectory})
    
    # Initiate driver
    driver = webdriver.Chrome(executable_path='Chromedriver/chromedriver.exe', options=chrome_options)
    
    # Return driver
    return(driver)

def ScrapeRedfinHousingMetrics(driver, neighborhood, housingMetrics, metricNames, chartName):
    
    # Select 5 years button
    driver.find_element_by_xpath('//*[@id="' + chartName + '"]/div[1]/div[2]/button[3]',).click()
    
    # Pause
    Pause.Small()
    
    # Scrape redfin housing metrics
    for metricName in metricNames:
        
        # Click metric
        driver.find_element_by_xpath('//*[@id="' + chartName + '"]/div[1]/div[1]/button/div/div[contains(text(), "' + metricName + '")]').click()
        
        # Set x offset value to 0
        offsetValue = 0
        
        # Create empty lists
        metricDates, metricValues = [list() for i in range(2)]
        
        # Scrape housing metrics by neighborhood
        while True:
            
            # Create action chain object
            action = ActionChains(driver)
            
            try:
                
                # Hover to the chart position
                action.move_to_element_with_offset(driver.find_element_by_xpath('//*[@id="' + chartName + '"]/div[3]/div/div/div[@class="VictoryContainer"]'), 16 + offsetValue, 0).perform()
                
                # Add date to list
                metricDates.append(driver.find_element_by_xpath('//*[@id="graph-flyout"]/div[1]').text)
                
                # Add chart value to list
                metricValues.append(driver.find_element_by_xpath('//*[@id="graph-flyout"]/div[2]/div[1]').text)
            
            except:
                
                # Print number of scraped dates
                print('Scraped ' + str(len(set(metricDates))) + ' unique dates for ' + metricName + ' in ' + neighborhood)
                
                break
            
            # Add to the x offset value
            offsetValue += 9.4
        
        # Add values to housing metrics
        housingMetrics = pd.concat([housingMetrics, pd.DataFrame({'Neighborhood':neighborhood, 'Metric_Name':metricName, 'Metric_Date':metricDates, 'Metric_Value':metricValues})])
    
    # Return housing metrics
    return(housingMetrics)

def ScrapeRedfinCompeteScores(driver, neighborhood, neighborhoodScores):
    
    # Find compete score
    metricValues = driver.find_element_by_xpath('//*[@id="compete"]/div[1]/div[1]').text
    
    # Add values to neighborhood scores
    neighborhoodScores = pd.concat([neighborhoodScores, pd.DataFrame({'Neighborhood':[neighborhood], 'Metric_Name':['Compete Score'], 'Metric_Value':[metricValues]})])
    
    # Print neighborhood scraped
    print('Scraped compete score for ' + neighborhood)
    
    # Return neighborhood score
    return(neighborhoodScores)

def ScrapeRedfinTransportationScores(driver, neighborhood, neighborhoodScores):
    
    # Click transportation section
    driver.find_element_by_xpath('//*[@id="null-collapsible"]/div[1]/div/div/div[1]/h2[contains(text(), "Transportation")]').click()
    
    # Set transportation section names
    scoreNames = ['Walk Score', 'Transit Score', 'Bike Score']
    
    # Create empty list
    scoreValues = list()
    
    # Scrape neighborhood scores
    for i in range(3):
        
        # Add values to score values
        scoreValues.append(driver.find_element_by_xpath('//*[@id="null-collapsible"]/div[2]/div/div/div[1]/div[@class="viz-container"]/div[' + str(i + 1) + ']/div[1]/div/span[1]').text)
    
    # Add values to neighborhood scores
    neighborhoodScores = pd.concat([neighborhoodScores, pd.DataFrame({'Neighborhood':neighborhood, 'Score_Name':scoreNames, 'Score_Value':scoreValues})])
    
    # Print neighborhood scraped
    print('Scraped transportation scores for ' + neighborhood)
    
    # Return neighborhood scores
    return(neighborhoodScores)

def DownloadRedfinHousingData(driver, downloadUrl, neighborhood, neighborhoodId, downloadDirectory):
    
    # Download last 5 years housing data
    driver.get(downloadUrl.replace('{neighborhood_id}', neighborhoodId))
    
    # Pause
    Pause.Large()
    
    # Identify latest file name
    latestFile = max(['/'.join(downloadDirectory) + "\\" + file for file in os.listdir('/'.join(downloadDirectory))], key=os.path.getctime)
    
    # Rename file to neighborhood name
    shutil.move(latestFile, os.path.join('/'.join(downloadDirectory), neighborhood + '.csv'))


# --- Redfin Neighborhood Id Scraping --- #

# Load neighborhoods
neighborhoods = pd.read_csv('Data/San Diego Neighborhoods.csv')

# Initiate driver
driver = InitiateDriver()

# Scrape neighborhood ids
for neighborhood in neighborhoods['Neighborhood_Name_Redfin']:
    
    # Load redfin neighborhood search
    driver.get('https://www.redfin.com/zipcode/92111/filter/viewport=32.90262:32.72257:-117.07402:-117.24018,no-outline')
    
    # Pause
    Pause.Medium()
    
    # Click search bar
    driver.find_element_by_xpath('//*[@id="headerUnifiedSearch"]/div/form/div/div/div/div').click()
    
    # Pause
    Pause.Small()
    
    # Type neighborhood in search
    driver.find_element_by_xpath('//*[@id="search-box-input"]').send_keys(neighborhood + ' San Diego, CA')
    
    # Pause
    Pause.Large()
    
    # Click top result
    driver.find_element_by_xpath('//*[@id="headerUnifiedSearch"]/div/form/div[3]/div[1]/div/div[2]/a').click()
    
    # Pause
    Pause.Medium()
    
    # Identify neighborhood id
    neighborhoodId = driver.current_url.split('/')[4]
    
    # Set neighborhood id
    neighborhoods.loc[(neighborhoods['Neighborhood'] == neighborhood), 'Neighborhood_Id_Redfin'] = neighborhoodId

# Write neighborhoods to a csv
neighborhoods.to_csv('San Diego Neighborhoods.csv', index=False)


# --- Train Data Scraping --- #

# Load neighborhoods
neighborhoods = pd.read_csv('Data/San Diego Neighborhoods.csv')

# Set download directory
downloadDirectory = ['Data', 'Model Data - Train']

# Load driver
driver = InitiateDriver('\\' + '\\'.join(downloadDirectory) + '\\')

# Filter duplicates
neighborhoods = neighborhoods[['Neighborhood', 'Neighborhood_Id_Redfin']].drop_duplicates()

# Scrape train data
for index, row in neighborhoods.iterrows():
    
    # Set download url
    downloadUrl = 'https://www.redfin.com/stingray/api/gis-csv?al=1&market=socal&min_stories=1&num_homes350&ord=redfin-recommended-asc&page_number=1&region_id={neighborhood_id}&region_type=1&sold_within_days=1825&status=9&uipt=1,2,3,4,5,6,7,8&v=8'
    
    # Download last 5 years housing data
    DownloadRedfinHousingData(driver, downloadUrl, row['Neighborhood'], str(row['Neighborhood_Id_Redfin']), downloadDirectory)


# --- Test Data Scraping --- #

# Load neighborhoods
neighborhoods = pd.read_csv('Data/San Diego Neighborhoods.csv')

# Set download directory
downloadDirectory = ['Data', 'Model Data - Test']

# Load driver
driver = InitiateDriver('\\' + '\\'.join(downloadDirectory) + '\\')

# Filter duplicates
neighborhoods = neighborhoods[['Neighborhood', 'Neighborhood_Id_Redfin']].drop_duplicates()

# Scrape train data
for index, row in neighborhoods.iterrows():
    
    # Set download url
    downloadUrl = 'https://www.redfin.com/stingray/api/gis-csv?al=1&market=socal&min_stories=1&num_homes=350&ord=redfin-recommended-asc&page_number=1&region_id={neighborhood_id}&region_type=1&sf=1,2,3,5,6,7&status=9&uipt=1,2,3,4,5,6,7,8&v=8'
    
    # Download last 5 years housing data
    DownloadRedfinHousingData(driver, downloadUrl, row['Neighborhood'], str(row['Neighborhood_Id_Redfin']), downloadDirectory)


# --- Redfin Market Insights Scraping --- #

# Set download directory
downloadDirectory = ['Data', 'Redfin Market Insights']

# Load driver
driver = InitiateDriver('\\' + '\\'.join(downloadDirectory) + '\\')

# Create empty data frames
housingMetrics = pd.DataFrame(columns = ['Neighborhood', 'Metric_Name', 'Metric_Date', 'Metric_Value'])
neighborhoodScores = pd.DataFrame(columns = ['Neighborhood', 'Metric_Name', 'Metric_Value'])

# Scrape market insights
for i in range(len(neighborhoods)):
    
    # Load market insights for neighborhood
    driver.get('https://www.redfin.com/neighborhood/' + str(neighborhoods['Neighborhood_Id_Redfin'][i]) + '/CA/San-Diego/Mission-Valley/housing-market')
    
    # Pause
    Pause.Large()
    
    try:

        # Scrape home prices metrics
        housingMetrics = ScrapeRedfinHousingMetrics(driver,
                                                    neighborhoods['Neighborhood_Label'][i],
                                                    housingMetrics,
                                                    ['Median Sale Price', '# of Homes Sold', 'Median Days on Market'],
                                                    'home_prices')
    except:
        
        # Go to next section
        pass
    
    try:
        
        # Scrape demand metrics
        housingMetrics = ScrapeRedfinHousingMetrics(driver,
                                                    neighborhoods['Neighborhood_Label'][i],
                                                    housingMetrics,
                                                    ['Sale-to-List Price', 'Homes Sold Above List Price', 'Homes with Price Drops'],
                                                    'demand')
    
    except:
        
        # Go to next section
        pass
    
    try:
        
        # Scrape compete scores
        neighborhoodScores = ScrapeRedfinCompeteScores(driver, neighborhoods['Neighborhood_Label'][i], neighborhoodScores)
        
    except:
        
        # Go to next section
        pass
    
    try:
        
        # Scrape transportation scores
        neighborhoodScores = ScrapeRedfinTransportationScores(driver, neighborhoods['Neighborhood_Label'][i], neighborhoodScores)
        
    except:
        
        # Go to next section
        pass

# Reset index for data frames
housingMetrics = housingMetrics.reset_index(drop=True)
neighborhoodScores = neighborhoodScores.reset_index(drop=True)

# Save data to pickle
housingMetrics.to_pickle('Data/Redfin Market Insights/Housing Metrics.pkl')
neighborhoodScores.to_pickle('Data/Redfin Market Insights/Neighborhood Scores.pkl')


# --- 2 Bed Housing Scraping --- #

# Set download directory
downloadDirectory = ['Data', 'Redfin Housing Data', '2 Bed Housing']

# Load driver
driver = InitiateDriver('\\' + '\\'.join(downloadDirectory) + '\\')

# Scrape last 5 years housing data
for i in range(len(neighborhoods)):
    
    # Set download url
    downloadUrl = 'https://www.redfin.com/stingray/api/gis-csv?al=1&market=socal&max_num_beds=2&min_stories=1&num_baths=2&num_beds=2&num_homes=350&ord=redfin-recommended-asc&page_number=1&region_id={neighborhood_id}&region_type=1&sold_within_days=1825&status=9&uipt=1,2,3,4,5,6,7,8&v=8'
    
    # Download last 5 years housing data
    DownloadRedfinHousingData(driver, downloadUrl, str(neighborhoods['Neighborhood_Id_Redfin'][i]), downloadDirectory)


# --- 3 Bed Housing Scraping --- #

# Set download directory
downloadDirectory = ['Data', 'Redfin Housing Data', '3 Bed Housing']

# Load driver
driver = InitiateDriver('\\' + '\\'.join(downloadDirectory) + '\\')

# Scrape last 5 years housing data
for i in range(len(neighborhoods)):
    
    # Set download url
    downloadUrl = 'https://www.redfin.com/stingray/api/gis-csv?al=1&market=socal&max_num_beds=3&min_stories=1&num_baths=2&num_beds=3&num_homes=350&ord=redfin-recommended-asc&page_number=1&region_id={neighborhood_id}&region_type=1&sold_within_days=1825&status=9&uipt=1,2,3,4,5,6,7,8&v=8'
    
    # Download last 5 years housing data
    DownloadRedfinHousingData(driver, downloadUrl, str(neighborhoods['Neighborhood_Id_Redfin'][i]), downloadDirectory)


# --- Crime Scraping --- #

# Load driver
driver = InitiateDriver('')

# Load crime data stats page
driver.get('http://crimestats.arjis.org/')

# Pause
Pause.Large()

# Click san diego county
driver.find_element_by_xpath('//*[@id="ddAgency"]/option[text()="San Diego"]').click()

# Pause
Pause.Small()

# Click button to open more options
driver.find_element_by_xpath('//*[@id="ImageButton1"]').click()

# Pause
Pause.Small()

# Set the area type
driver.find_element_by_xpath('//*[@id="ddGeoArea"]/option[text()="NEIGHBORHOOD"]').click()

# Pause
Pause.Small()

# Click the submit button
driver.find_element_by_xpath('//*[@id="btnSubmit"]').click()

# Pause
Pause.Small()

# Create a list of dates
dateOptions = [option.text for option in driver.find_elements_by_xpath('//*[@id="ddBeginDate"]/option')][2:]

# Create empty data frame
crimeStats = pd.DataFrame(columns = ['Neighborhood', 'Date', 'Crime', 'Count'])

for dateOption in dateOptions:
    
    driver.find_element_by_xpath('//*[@id="ddBeginDate"]/option[text()="' + dateOption + '"]').click()
    
    Pause.Small()
    
    for tryNum in range(5):
        
        try:
            
            # Click the submit button
            driver.find_element_by_xpath('//*[@id="btnSubmit"]').click()
            
            # Break out of loop
            break
        
        except Exception as error:
            
            # Save error
            savedError = error
           
            # Pause
            Pause.Medium()
           
            # Go to next loop
            pass
    
    else:
       
        # Raise error
        raise savedError
    
    # Pause
    Pause.Large()
    
    try:
        
        # Read html table
        crimeStatsTable = pd.read_html(driver.find_element_by_xpath('//*[@id="G_UltraWebTab1xctl00xWebDataGrid1"]').get_attribute('outerHTML'))[0]
        
    except:
        
        # Go to next date
        continue
    
    # Convert crime stats to a long version
    crimeStatsTable = crimeStatsTable.melt(id_vars='Crime', value_vars=crimeStatsTable.columns[1:])
    
    # Add date to data frame
    crimeStatsTable['Date'] = dateOption
    
    # Rename columns
    crimeStatsTable = crimeStatsTable.rename(columns={'variable': 'Neighborhood', 'value': 'Count'})
    
    # Append crime stats table to data frame
    crimeStats = pd.concat([crimeStats, crimeStatsTable])




