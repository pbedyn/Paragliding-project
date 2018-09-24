# -*- coding: utf-8 -*-
"""
Created on Tue Jun  5 10:17:22 2018

@author: BedynskiPa01
"""

### TODO: Create a pop up to specify the site and the download folder
### TODO: Export a gpx file that will indicate most probable thermal sources for a specific day
### TODO: Identify a thermal based on track
### TODO: Clean up the code, objectify it
### TODO: Implement parallel processing to spool data in parallel for multiple take offs
### TODO: Apply a machine learning algorithm to identify turns and thermals
### TODO: Create a flight replayer to see if identification of flight parameters works

import pandas as pd
import os
from os import path
import requests

## read content of all flights from Borsk and save in the Borsk.txt file for further extraction of individual igc files
path2data = 'C:/Users/bedynskipa01/Documents/09. Hobby/Flights/'
summary_file = "Roldanillo.txt"

################# This section extracts data from the xcportal website and saves all files from a given location #############
################# Need to know the node which has to be extracted manually


L_tracks = []
summary_file_path = path2data + summary_file
url = "http://xcportal.pl/node/40056?order=field_flight_max_points&sort=desc"
       
try:
    url = "http://xcportal.pl/node/40056?order=field_flight_max_points&sort=desc"
    r = requests.get(url, stream = True)
    with open(summary_file_path, 'a') as the_file:
        the_file.write(r.text)
except:
    print("Last file in history")

## create a list of nodes of all flights from Borsk
with open(summary_file_path, 'r') as f:
    for line in f:
        for word in line.split():
            if word.find('node') == 7:
                if word[17] == '"':
                    L_tracks.append(word[7:17])
                else:
                    L_tracks.append(word[7:18])

## go through the nodes to extract direct paths to igc files
L_igcs = []
for x in L_tracks[1:]:
    url = "http://xcportal.pl/" + x
    file_path = path2data + str(L_tracks.index(x)) + ".txt"
    try:
        r = requests.get(url, stream = True)
        with open(file_path, 'w') as the_file:
            the_file.write(r.text)
    except:
        print("I've done nothing")
    
    with open(file_path, 'r') as f:
        for line in f:
            for word in line.split():
                if word.find('href=') == 0 and word[len(word)-5:len(word)] == '.igc"':
                    L_igcs.append(word[6:len(word)-1])
    """ remove all temporay files created during execution of the loop """
    os.remove(file_path)

### save all files in the given directory - in this example in the Borsk directory
for igc in L_igcs[:]:
    url = igc
    file_path = path2data + "Roldanillo/" + str(L_igcs.index(igc)) + ".txt"
    try:
        r = requests.get(url, stream = True)
        with open(file_path, 'w', encoding="utf-8") as the_file: ## the encoding command handles polish characters
            the_file.write(r.text)
    except:
        print("Last file in history")
        
################# This section extracts basic parameters from the files and converts them into a pandas dataframe #############

""" How to go through all files in a directory """
columns = ['Pilot name', 'Date', 'Time', 'Glider', 'Datum', 'Latitude', 'Lat_orient', 'Longitude', 'Lon_orient', 'Bar Alt', 'GPS Alt', 'Distance']
df = pd.DataFrame(columns = columns)


### this loop goes through all files and appends the motherfather of a dataframe
for i in range(2000, 2001):
        file_path = path2data + "Roldanillo/" + str(i) + ".txt"
        with open(file_path, 'r') as f:
            for line in f:
                if line[0:5] == "HFDTE":
                    flight_date = line[5:len(line)]
                else:
                    next
                if line[5:10] == "PILOT":
                    pilot_name = line[11:len(line)]
                else:
                    next
                
                if line[5:15] == "GLIDERTYPE":
                    glider = line[16:len(line)]
                else:
                    next
                
                if line[5:16] == "100GPSDATUM":
                    datum = line[17:len(line)]
                else:
                    next
                
                if line[0:1] == "B":
                    flight_time = line[1:7]
                    latitude = line[7:14]
                    lat_orient = line[14:15]                    
                    longitude = line[15:23]
                    lon_orient = line[23:24]
                    bar_alt = line[25:30]
                    gps_alt = line[31:35]
                    df = df.append({'Pilot name': pilot_name,
                                     'Date': flight_date,
                                     'Time': flight_time,
                                     'Glider': glider,
                                     'Datum': datum,
                                     'Latitude': latitude,
                                     'Lat_orient': lat_orient,
                                     'Longitude': longitude,
                                     'Lon_orient': lon_orient,
                                     'Bar Alt': bar_alt,
                                     'GPS Alt': gps_alt}, ignore_index = True)
                                                    
import math
import numpy as np
from decimal import Decimal

""" calculate time in seconds between records """
""" calculate distance in meters between records """
""" impute data to fill in the gaps (simple linear distance way first) """
""" impute data to fill in the gaps (detect turns and use arcs to fill in the gaps) """

""" extract degrees from columns Latitude and Longitude """
df['Latitude'] = df['Latitude'].astype(float)
df['Latitude'] = df['Latitude'] / 100000.0

df['Longitude'] = df['Longitude'].astype(float)
df['Longitude'] = df['Longitude'] / 100000.0

df['Bar Alt'] = df['Bar Alt'].astype(float)
df['GPS Alt'] = df['GPS Alt'].astype(float)

df['Lat_shifted'] = df['Latitude'].shift(1)
df['Lon_shifted'] = df['Longitude'].shift(1)
df['Lat_shifted'].fillna(df['Latitude'], inplace = True)
df['Lon_shifted'].fillna(df['Longitude'], inplace = True)

### Calculate distance between two points using the Haversine formula
### a = math.sin(del_phi / 2.0) * math.sin(del_phi / 2.0) + \
###    math.cos(phi_1) * math.cos(phi_2) * math.sin(del_lbd / 2.0) * math.sin(del_lbd / 2.0)
### c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))
### d = R * c

R = 6371000 ### TODO: Calculate Earth's radius for a given latitude
df['phi_1'] = df['Latitude'].apply(math.radians)
df['phi_2'] = df['Lat_shifted'].apply(math.radians)

df['del_phi'] = df['Lat_shifted'] - df['Latitude']
df['del_phi'] = df['del_phi'].apply(math.radians) / 2.0

df['del_lbd'] = df['Lon_shifted'] - df['Longitude']
df['del_lbd'] = df['del_lbd'].apply(math.radians) / 2.0

df['a'] = np.sin(df['del_phi']) * np.sin(df['del_phi']) + \
          np.cos(df['phi_1']) * np.cos(df['phi_2']) * \
          np.sin(df['del_lbd']) * np.sin(df['del_lbd'])

df['sqrt_a'] = np.sqrt(df['a'])
df['one'] = 1.0
df['one'] = df['one'].apply(Decimal)
df['sqrt_1-a'] = np.sqrt(np.subtract(df['one'], df['a'].apply(Decimal)))

df['c'] = 2.0 * np.arctan2(df['sqrt_a'], df['sqrt_1-a'].astype(float))
df['Distance'] = R * df['c']
  
### Do a bit of clean up
df = df.drop(columns = ['phi_1', 'phi_2', 'del_phi', 'del_lbd', 'a', 'sqrt_a', 'sqrt_1-a', 'one', 'c'])
sum(df['Distance'])

### Append the first row to the table
df = df.append(df.iloc[0,])
### Shift longitude and latitude for the calculation of the polygon centre
df['Lat_shifted'] = df['Latitude'].shift(1)
df['Lon_shifted'] = df['Longitude'].shift(1)
df['Lat_shifted'].fillna(df['Latitude'], inplace = True)
df['Lon_shifted'].fillna(df['Longitude'], inplace = True)

df['auxiliary'] = df['Lat_shifted'] * df['Longitude'] - df['Lon_shifted'] * df['Latitude']
df['aux_Cx'] = df['Lat_shifted'] + df['Latitude']
df['aux_Cy'] = df['Lon_shifted'] + df['Longitude']
Cx = 1.0 / (3 * sum(df['auxiliary'][1:len(df) + 1,])) * sum(df['aux_Cx'][1:len(df) + 1,] * df['auxiliary'][1:len(df) + 1,])
Cy = 1.0 / (3 * sum(df['auxiliary'][1:len(df) + 1,])) * sum(df['aux_Cy'][1:len(df) + 1,] * df['auxiliary'][1:len(df) + 1,])


### Calculate bearing in degrees
df['dLon'] = df['Longitude'].apply(math.radians) - df['Lon_shifted'].apply(math.radians)
df['y'] = np.sin(df['dLon']) * np.cos(df['Latitude'].apply(math.radians))
df['x'] = np.sin(df['Latitude'].apply(math.radians)) * np.cos(df['Lat_shifted'].apply(math.radians)) - \
    np.sin(df['Lat_shifted'].apply(math.radians)) * np.cos(df['Latitude'].apply(math.radians)) * np.cos(df['dLon'])
df['Bearing'] = np.arctan2(df['y'], df['x']).apply(math.degrees)
df['Bearing'] = np.where(df['Bearing'] < 0, df['Bearing'] + 360.0, df['Bearing'])

### Determine when the given path makes a circle and when it does calculate the centre of the polygon
### TODO: Turn determination of the circle into a function
### TODO: Determine altitude gain and start tracking circles when vertical speed reaches 0.5 m/s