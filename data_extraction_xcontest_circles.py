# -*- coding: utf-8 -*-
"""
Created on Thu Oct  4 18:35:53 2018
@author: Pawel Bedynski
"""

### TODO: Save flights that have not been scraped to a file for future reference
### TODO: Automatically discover how many flights are on the page and scrape all into a list
### TODO: Automatically detect the environment (lattepanda and my usual computer) and
###       automatically modify paths to folders and chromedrivers
### TODO: Determine length of the flight and scrape only those longer than e.g. 10km

### import standard Python libraries for execution
import os
import time
from random import randint

### import webscraping libraries
import requests

### set path to a folder in Downloads where all tracks will be stored
def set_paths():
    path2data = 'C:\\Users\\pawel\\Downloads\\flights\\'
    path2file = 'C:\\Users\\pawel\\Downloads\\flights\\New Batch\\'
    path2drivers = "C:\\Users\\pawel\\Downloads\\flights\\ChromeDrivers\\"    
    if not os.path.exists(path2data):
        path2data = 'C:\\Users\\lattepanda\\Downloads\\flights\\'    
        path2file = 'C:\\Users\\lattepanda\\Downloads\\flights\\New Batch\\'
        path2drivers = "C:\\Users\\lattepanda\\Downloads\\flights\\ChromeDrivers\\"
    return path2data, path2file, path2drivers

### Identify digits in the string        
def get_digits(string):
    c = ""
    for i in string:
        if i.isdigit():
            c += i
    return c

### Scrape only links to flights within circles
def scrape_flight_links(path2data, longitude, latitude, radius):
    
    summary_file = str(longitude) + "_" + str(latitude) + ".txt"
    summary_file_path = path2data + summary_file
    
    ## This handles the first page of 50 flights
    url = "https://www.xcontest.org/world/en/flights-search/?list[sort]=pts&filter[point]="
    url = url + str(longitude) + "+" + str(latitude) + "&filter%5Bradius%5D=" + str(radius)
    url = url + "&filter[mode]=START&filter[date_mode]=dmy&filter[date]=&"
    url = url + "filter[value_mode]=dst&filter[min_value_dst]=&filter[catg]=&filter[route_types]="
    url = url + "&filter[avg]=&filter[pilot]="
    try:
        r = requests.get(url)
        with open(summary_file_path, 'w', encoding='utf-8') as the_file:
            the_file.write(r.text)
    except:
        print("Last file in history")
    
    ### This finds the number of flights and determines loop end for the next step
    number_of_flights = 0
    with open(summary_file_path, 'r', encoding='utf-8') as f:
        for line in f:
            for word in line.split():
                if word.find('style="vertical-align:baseline') == 0:
                    number_of_flights = int(get_digits(word))
                    break
    print(number_of_flights)
    
    ### Calculate loop_end
    loop_end = int(number_of_flights / 50) + 1
    
    ## Scrolls through pages of flights in xcontest 50 at a time and scrapes their content
    ## to get links to individual flights.
    for i in range(1, loop_end):
        time.sleep(randint(3, 12))
        url = "https://www.xcontest.org/world/en/flights-search/?list[sort]=pts&list[start]=" 
        url = url + str(i * 50)
        url = url + "&filter[point]="
        url = url + str(longitude) + "+" + str(latitude) + "&filter%5Bradius%5D=" + str(radius)
        url = url + "&filter[mode]=START&filter[date_mode]=dmy&filter[date]=&filter[value_mode]="
        url = url + "dst&filter[min_value_dst]=&filter[catg]=&filter[route_types]=&filter[avg]=&filter[pilot]="
        try:
            r = requests.get(url)
            with open(summary_file_path, 'a', encoding='utf-8') as the_file:
                the_file.write(r.text)
        except:
            print("Last file in history")
            
###############################################################################
# execution of the mian part of the program ###################################    
if __name__ == "__main__":

    # set paths
    path2data, path2file, path2drivers = set_paths()
    
    radius = 200000
    for longitude in range(9, 11, 2): # 5 - 13
        for latitude in range(35, 59, 2): #35 - 59
            scrape_flight_links(path2data, longitude, latitude, radius)
    
    
