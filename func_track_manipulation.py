# -*- coding: utf-8 -*-
"""
Created on Fri Oct 19 20:42:58 2018

@author: BedynskiPa01
"""
### TODO
### create functions for the specific tasks
### function to calculate instantaneout velocity - DONE
### function to calculate instantaneous bearing - DONE
### function to calculate distance traveled between readings - DONE
### function to calculate height gain - DONE
### function to calculate vertical speed - DONE
### function to calculate wind speed
### function to calculate wind direction
### function to calculate centre of a centroid
### use google api to place centres of centroids on a map

### create a function identifying sources of thermals
### extract date and flight time while reading the file

import pandas as pd
import numpy as np

## Create a folder in Downloads where all tracks will be stored
path2data = 'C:\\Users\\bedynskipa01\\Downloads\\Flights\\'
summary_file = "Roldanillo.txt"
summary_file_path = path2data + summary_file

###############################################################################
###############################################################################
###############################################################################
def haversine(lon1, lat1, lon2, lat2):
    """
    Vectorized version of distance calculation based on the haversine formula
    Takes 4 parameters where lon1, lat1 are coordinates of starting points
    And lon2, lat2 are coordinates of the finish points (specified in decimal degrees)
    """
    # convert decimal degrees to radians 
    lon1, lat1, lon2, lat2 = map(np.radians, [lon1, lat1, lon2, lat2])

    # haversine formula 
    dlon = lon2 - lon1 
    dlat = lat2 - lat1 
    a = np.sin(dlat/ 2.0)**2 + np.cos(lat1) * np.cos(lat2) * np.sin(dlon/ 2.0)**2
    c = 2.0 * np.arcsin(np.sqrt(a)) 
    r = 6371.0 # Radius of earth in miles. Use 3956 for miles
    return c * r

###############################################################################
###############################################################################
###############################################################################
def bearing(lon1, lat1, lon2, lat2):
    """
    Vectorized version of the initial bearing calculation based on the forward 
    azimuth formula
    Takes 4 parameters where lon1, lat1 are coordinates of starting points
    And lon2, lat2 are coordinates of the finish points (specified in decimal degrees)
    """
    # convert decimal degrees to radians 
    lon1, lat1, lon2, lat2 = map(np.radians, [lon1, lat1, lon2, lat2])

    # forward azimuth formula 
    dlon = lon2 - lon1 
    y = np.sin(dlon) * np.cos(lat2)
    x = np.cos(lat1) * np.sin(lat2) - np.sin(lat1) * np.cos(lat2) * np.cos(dlon)
    brng = np.degrees(np.arctan2(y, x))
    return np.mod(brng + 360.0, 360.0) ## convert the outcome to degrees

###############################################################################
###############################################################################
###############################################################################
def inst_vel_km_per_h(distance, time):
    """
    Vectorized version of instanteneous velocity calculation
    Takes distance in km, time in seconds and calculates velocity in km/h
    """
    time_hours = time / 3600.0
    return distance / time_hours

###############################################################################
###############################################################################
###############################################################################
def inst_vel_m_per_s(distance, time):
    """
    Vectorized version of instanteneous velocity calculation
    Takes distance in metres, time in seconds and calculates velocity in m/s
    """
    return distance / time

###############################################################################
###############################################################################
###############################################################################
def calc_distance(df):
    ''' Function takes a data frame containing latitude and longitude
        and calculates distance between consecutive points using gps 
        coordinates and stores it in column "distance" of the data frame
        it uses the vectorized haversine function
        End points are start points shifted by one position
    '''
    ## data preparation (create new column, shift coordinates, clean up zeros)
    df['lat_shifted'] = df['latitude'].shift(1)
    df['lat_shifted'][df['lat_shifted'].isnull()] = df['latitude']
    df['lon_shifted'] = df['longitude'].shift(1)
    df['lon_shifted'][df['lon_shifted'].isnull()] = df['longitude']
    ## use the vectorized haversine function
    return haversine(df['longitude'], df['latitude'], df['lon_shifted'], df['lat_shifted'])
    
###############################################################################
###############################################################################
###############################################################################
def calc_bearing(df):
    ''' Function takes a data frame containing latitude and longitude
        and calculates distance between consecutive points using gps 
        coordinates and stores it in column "distance" of the data frame
        it uses the vectorized haversine function
        End points are start points shifted by one position
    '''
    ## data preparation (create new column, shift coordinates, clean up zeros)
    df['bearing'] = 0
    df['lat_shifted'] = df['latitude'].shift(1)
    df['lat_shifted'][df['lat_shifted'].isnull()] = df['latitude']
    df['lon_shifted'] = df['longitude'].shift(1)
    df['lon_shifted'][df['lon_shifted'].isnull()] = df['longitude']
    ## use the vectorized forward azimuth function
    return bearing(df['longitude'], df['latitude'], df['lon_shifted'], df['lat_shifted'])
    
###############################################################################
###############################################################################
###############################################################################
def calc_velocity(df):
    ''' Function takes a distance and time and calculates velocity
    '''
    ## data preparation (create new columns, shift time, take care of nans)
    return inst_vel_km_per_h(df['distance'], df['time_diff'])

###############################################################################
###############################################################################
###############################################################################
def calc_height_gain(df, height_type):
    ''' Function calculates height type for barographic (bar_alt) or 
        gps altitude (gps_alt)
    '''
    ## data preparation (create new columns, shift time, take care of nans)
    if height_type == "bar_alt":
        df['bar_alt_shifted'] = 0
        df['bar_alt_shifted'] = df['bar_alt'].shift(1)
        df['bar_alt_diff'] = df['bar_alt'] - df['bar_alt_shifted']
        df['bar_alt_diff'][df['bar_alt_diff'] > 20] = 0
        df['bar_alt_diff'][df['bar_alt_diff'] < -20] = 0
        df['bar_alt_diff'][df['bar_alt_diff'].isnull()] = 0
        return df['bar_alt_diff']
    elif height_type == "gps_alt":
        df['gps_alt_shifted'] = 0
        df['gps_alt_shifted'] = df['gps_alt'].shift(1)
        df['gps_alt_diff'] = df['gps_alt'] - df['gps_alt_shifted'] 
        df['gps_alt_diff'][df['gps_alt_diff'] > 20] = 0
        df['gps_alt_diff'][df['gps_alt_diff'] < -20] = 0
        df['gps_alt_diff'][df['gps_alt_diff'].isnull()] = 0
        return df['gps_alt_diff']