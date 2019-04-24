# -*- coding: utf-8 -*-
"""
Created on Fri Nov  2 18:27:15 2018
@author: Pawel Bedynski
Assumes there is the frame file in the folder. Reads the frame file
Calculates grids by hour and each 10 minutes interval and saves them 
into npz formats to save space

Note that there are several methods:
    process_lift_hours
    process_sink_hours
    process_lift_minutes
    process_sink_minutes
    process_circles
    process_wind
"""
from datetime import datetime
## packages to move files from one folder to another
import glob
import os.path

### import pandas and numpy
import pandas as pd
import numpy as np

### import warnings to suppress warnings during execution
import warnings
warnings.filterwarnings("ignore")


### Determine the leftmost bottom corner of the grid
def min_grid(grid_folders):
    grid_NS = []
    grid_EW = []
    for grid_folder in grid_folders:
        grid_NS.append(int(grid_folder[len(grid_folder) - 8: len(grid_folder) - 5]))
        grid_EW.append(int(grid_folder[len(grid_folder) - 4: len(grid_folder) - 1]))
    return (min(grid_NS) - 1) * 1000, (min(grid_EW) - 1)* 1000

###############################################################################
###############################################################################
### Function to process the given folder, create grids per hour
### This step is executed before data visualization step
def process_lift(df, grid_folder, min_NS, min_EW):   
    ### Create a grid of one 10000ths of a decimal degree as the playground to store
    ### information about thermals
    ### This is equivalent to a grid of approximately 100 meters by 100 meters
    ### calculate the hours of day to run iterations over
    
    ### set minimum for the North-South grid
    ### set minimum for the West-East grid
    
    grid = np.zeros(shape = (10000, 10000))
    gps_alt_vel = df['gps_alt_vel']
    NS_grid = df['NS_grid']
    EW_grid = df['EW_grid']
    
    for i in range(len(df)):
        ### 5000 ensures that vast majority of observations fit into the 10000 by 10000 grid
        ### this means precision of this grid is approx. 200 meters
        row = NS_grid[i] - min_NS
        column = EW_grid[i] - min_EW
        if (0 <= column < 9996) and (0 <= row < 9996):
            ### Whenever there is a thermal I'm adding some height also to the surrounding area
            ### The first grid gets highest increment, grids surrounding get 0.2 of the increment
            ### And grids further away get 0.33 of the increment
            ### Working here with gps_alt_vel which is TIME NORMALIZED
            if gps_alt_vel.values[i] > 0:
                for j in range(-3, 4):
                    for k in range(-3, 4):
                        if abs(j) <= 1 and abs(k) <= 1:
                            grid[row + j, column + k] = grid[row + j, column + k] + gps_alt_vel.values[i]
                        elif abs(j) <= 2 and abs(k) <=2:
                            grid[row + j, column + k] = grid[row + j, column + k] + 0.2 * gps_alt_vel.values[i]
                        else:
                            grid[row + j, column + k] = grid[row + j, column + k] + 0.1 * gps_alt_vel.values[i]
    ### save the grid file
    array_name = "grid_lift"
    np.savez_compressed(grid_folder + array_name + ".npz", name = grid)

###############################################################################
###############################################################################
### Function to process the given folder, create grids per hour
### This step is executed before data visualization step
def process_lift_hours(df):   
    ### Create a grid of one 10000ths of a decimal degree as the playground to store
    ### information about thermals
    ### This is equivalent to a grid of approximately 100 meters by 100 meters
    ### calculate the hours of day to run iterations over
    hour_of_day = df['hour'].unique()
    hour_of_day.sort()
    
    for hour in range(len(hour_of_day)):
        grid = np.zeros(shape = (10000, 10000))
        longitude = df['longitude'][df['hour'] == hour_of_day[hour]]
        latitude = df['latitude'][df['hour'] == hour_of_day[hour]]
        gps_alt_vel = df['gps_alt_vel'][df['hour'] == hour_of_day[hour]]
        for i in range(len(longitude)):
            ### 5000 ensures that vast majority of observations fit into the 10000 by 10000 grid
            ### this means precision of this grid is approx. 200 meters
            column = int(round(5000 * (longitude.values[i] - 74.4), 0))
            row = int(round(5000 * (latitude.values[i] - 3.2), 0))
            if (0 <= column < 9996) and (0 <= row < 9996):
                ### Whenever there is a thermal I'm adding some height also to the surrounding area
                ### The first grid gets highest increment, grids surrounding get 0.2 of the increment
                ### And grids further away get 0.33 of the increment
                ### Working here with gps_alt_vel which is TIME NORMALIZED
                if gps_alt_vel.values[i] > 0:
                    for j in range(-3, 4):
                        for k in range(-3, 4):
                            if abs(j) <= 1 and abs(k) <= 1:
                                grid[row + j, column + k] = grid[row + j, column + k] + gps_alt_vel.values[i]
                            elif abs(j) <= 2 and abs(k) <=2:
                                grid[row + j, column + k] = grid[row + j, column + k] + 0.2 * gps_alt_vel.values[i]
                            else:
                                grid[row + j, column + k] = grid[row + j, column + k] + 0.1 * gps_alt_vel.values[i]
        ### save the grid file
        array_name = "grid_lift" + str(hour_of_day[hour])
        np.savez_compressed(path2data + folder_name + "\\" + array_name + ".npz", name = grid)

###############################################################################
###############################################################################
### Function to process the given folder, create grids per minute
### This step is executed before data visualization step                        
def process_lift_minutes(df):
    ### sum up vertical velocity within grids
    ### 
    
    ### clean up the grid numbers
    df['EW_grid'][df['EW_grid'] <= 0] = 2
    df['EW_grid'][df['EW_grid'] >= 9998] = 9997
    
    df['NS_grid'][df['NS_grid'] <= 0] = 2
    df['NS_grid'][df['NS_grid'] >= 9998] = 9997
    
    ### calculate sum of gps_alt_vel
    summary = (df[df['gps_alt_vel'] > 0].groupby(['date', 'hour_minute', 'NS_grid', 'EW_grid'], as_index=False)
                    .agg({'gps_alt_vel': [('_sum', lambda x:np.sum(x))]}))
    summary.columns = list(map(''.join,summary.columns.values))
    ### merge this sum with the original dataframe
    df = pd.merge(df, summary,
                    how='left', 
                    on=['date', 'hour_minute', 'NS_sm_grid', 'EW_sm_grid'],
                    sort=False)
    
    ### calculate sum of bar_alt_vel
    ### summary = (df[df['bar_alt_vel'] == True].groupby(['date', 'hour_minute', 'NS_sm_grid', 'EW_sm_grid'], as_index=False)
    ###             .agg({'bar_alt_vel': [('_sum', lambda x:np.sum(x))]}))
    ### summary.columns = list(map(''.join,summary.columns.values))
    ### merge this sum with the original dataframe
    ### df = pd.merge(df, summary,
    ###                        how='left', 
    ###                        on=['date', 'hour_minute', 'NS_sm_grid', 'EW_sm_grid'],
    ###                        sort=False)
    ### seperate days of month
    day_of_month = df['date'].unique()
    day_of_month.sort()
    
    ### run analysis for each day of month
    for day in range(len(day_of_month)):
        day_of_month_folder = str(day_of_month[day])
        os.makedirs(path2data + folder_name + "\\days_of_month\\" + day_of_month_folder)
        df_day_of_month = df[df['date'] == day_of_month[day]]
        ### seperate minute of day
        hour_minute_of_day = df_day_of_month['hour_minute'].unique()
        hour_minute_of_day.sort()
        ### run analysis for each minute of day
        for hour_minute in range(len(hour_minute_of_day)):
            grid = np.zeros(shape = (10000, 10000))
            df_hour_minute = df_day_of_month[df_day_of_month['hour_minute'] == hour_minute_of_day[hour_minute]]
            try:
                ### cell with lift
                grid[df_hour_minute['NS_grid'], df_hour_minute['EW_grid']] = df_hour_minute['gps_alt_vel_sum']
                ### 8 cells one from the one with lift
                grid[df_hour_minute['NS_grid'] + 1, df_hour_minute['EW_grid']] += 0.2 * df_hour_minute['gps_alt_vel_sum']
                grid[df_hour_minute['NS_grid'] + 1, df_hour_minute['EW_grid'] + 1] += 0.2 * df_hour_minute['gps_alt_vel_sum']
                grid[df_hour_minute['NS_grid'] + 1, df_hour_minute['EW_grid'] - 1] += 0.2 * df_hour_minute['gps_alt_vel_sum']
                grid[df_hour_minute['NS_grid'] - 1, df_hour_minute['EW_grid']] += 0.2 * df_hour_minute['gps_alt_vel_sum']
                grid[df_hour_minute['NS_grid'] - 1, df_hour_minute['EW_grid'] + 1] += 0.2 * df_hour_minute['gps_alt_vel_sum']
                grid[df_hour_minute['NS_grid'] - 1, df_hour_minute['EW_grid'] - 1] += 0.2 * df_hour_minute['gps_alt_vel_sum']
                grid[df_hour_minute['NS_grid'], df_hour_minute['EW_grid'] - 1] += 0.2 * df_hour_minute['gps_alt_vel_sum']
                grid[df_hour_minute['NS_grid'], df_hour_minute['EW_grid'] + 1] += 0.2 * df_hour_minute['gps_alt_vel_sum']
                ### 16 cells two from the one with lift
                grid[df_hour_minute['NS_grid'] + 2, df_hour_minute['EW_grid'] - 2] += 0.1 * df_hour_minute['gps_alt_vel_sum']
                grid[df_hour_minute['NS_grid'] + 2, df_hour_minute['EW_grid'] - 1] += 0.1 * df_hour_minute['gps_alt_vel_sum']
                grid[df_hour_minute['NS_grid'] + 2, df_hour_minute['EW_grid']] += 0.1 * df_hour_minute['gps_alt_vel_sum']
                grid[df_hour_minute['NS_grid'] + 2, df_hour_minute['EW_grid'] + 1] += 0.1 * df_hour_minute['gps_alt_vel_sum']
                grid[df_hour_minute['NS_grid'] + 2, df_hour_minute['EW_grid'] + 2] += 0.1 * df_hour_minute['gps_alt_vel_sum']
                
                grid[df_hour_minute['NS_grid'] + 1, df_hour_minute['EW_grid'] - 2] += 0.1 * df_hour_minute['gps_alt_vel_sum']
                grid[df_hour_minute['NS_grid'], df_hour_minute['EW_grid'] - 2] += 0.1 * df_hour_minute['gps_alt_vel_sum']
                grid[df_hour_minute['NS_grid'] - 1, df_hour_minute['EW_grid'] - 2] += 0.1 * df_hour_minute['gps_alt_vel_sum']
                grid[df_hour_minute['NS_grid'] + 1, df_hour_minute['EW_grid'] + 2] += 0.1 * df_hour_minute['gps_alt_vel_sum']
                grid[df_hour_minute['NS_grid'], df_hour_minute['EW_grid'] + 2] += 0.1 * df_hour_minute['gps_alt_vel_sum']
                grid[df_hour_minute['NS_grid'] - 1, df_hour_minute['EW_grid'] + 2] += 0.1 * df_hour_minute['gps_alt_vel_sum']
                
                grid[df_hour_minute['NS_grid'] - 2, df_hour_minute['EW_grid'] - 2] += 0.1 * df_hour_minute['gps_alt_vel_sum']
                grid[df_hour_minute['NS_grid'] - 2, df_hour_minute['EW_grid'] - 1] += 0.1 * df_hour_minute['gps_alt_vel_sum']
                grid[df_hour_minute['NS_grid'] - 2, df_hour_minute['EW_grid']] += 0.1 * df_hour_minute['gps_alt_vel_sum']
                grid[df_hour_minute['NS_grid'] - 2, df_hour_minute['EW_grid'] + 1] += 0.1 * df_hour_minute['gps_alt_vel_sum']
                grid[df_hour_minute['NS_grid'] - 2, df_hour_minute['EW_grid'] + 2] += 0.1 * df_hour_minute['gps_alt_vel_sum']
                
                array_name = "grid_lift_" + str(hour_minute_of_day[hour_minute])
                np.savez_compressed(path2data + folder_name + "\\days_of_month\\" + \
                                    day_of_month_folder + "\\" + array_name + ".npz", name = grid)
            except:
                pass
    return df

###############################################################################
###############################################################################
### Function to process the given folder, create grids per hour
### This step is executed before data visualization step
def process_sink_hours(df):   
    ### Create a grid of one 10000ths of a decimal degree as the playground to store
    ### information about sink holes
    ### This is equivalent to a grid of approximately 100 meters by 100 meters
    ### calculate the hours of day to run iterations over
    hour_of_day = df['hour'].unique()
    hour_of_day.sort()
    
    for hour in range(len(hour_of_day)):
        grid = np.zeros(shape = (10000, 10000))
        longitude = df['longitude'][df['hour'] == hour_of_day[hour]]
        latitude = df['latitude'][df['hour'] == hour_of_day[hour]]
        gps_alt_vel = df['gps_alt_vel'][df['hour'] == hour_of_day[hour]]
        for i in range(len(longitude)):
            ### 5000 ensures that vast majority of observations fit into the 10000 by 10000 grid
            column = int(round(5000 * (longitude.values[i] - 74.4), 0))
            row = int(round(5000 * (latitude.values[i] - 3.2), 0))
            if (0 <= column < 9996) and (0 <= row < 9996):
                ### Whenever there is a thermal I'm adding some height also to the surrounding area
                ### The first grid gets highest increment, grids surrounding get 0.2 of the increment
                ### And grids further away get 0.33 of the increment
                ### Working here with gps_alt_vel which is TIME NORMALIZED
                if gps_alt_vel.values[i] < 0:
                    for j in range(-3, 4):
                        for k in range(-3, 4):
                            if abs(j) <= 1 and abs(k) <= 1:
                                grid[row + j, column + k] = grid[row + j, column + k] + gps_alt_vel.values[i]
                            elif abs(j) <= 2 and abs(k) <=2:
                                grid[row + j, column + k] = grid[row + j, column + k] - 0.2 * gps_alt_vel.values[i]
                            else:
                                grid[row + j, column + k] = grid[row + j, column + k] - 0.1 * gps_alt_vel.values[i]                  

        ### save the grid file
        array_name = "grid_sink" + str(hour_of_day[hour])
        np.savez_compressed(path2data + folder_name + "\\" + array_name + ".npz", name = grid)
    
###############################################################################
###############################################################################
### This function tests for circle in a given minute and saves result
### for that group in the data frame. It is used by the process_circles function
def is_circle(grp):
    if np.any(grp['bearing'] > 180) and np.any(grp['bearing'] <= 180) and np.any(grp['velocity'] > 5):
        grp['circle'] = True
    else:
        grp['circle'] = False
    return grp
    
###############################################################################
###############################################################################
### Function processes circles
def process_circles(df):    
    ### add the circle column
    df['circle'] = False
    ### split apply combine at its finest:
    df = df.groupby(['flight_no', 'hour_minute']).apply(is_circle)
    return df

###############################################################################
###############################################################################
### Function to process the given folder, create grids per hour
### This step is executed before data visualization step
def find_wind_dir_and_speed(grp):
    try:
        max_velocity = max(grp['velocity'][grp['circle'] == True])
        ### take the first element of the series if there are more than one
        ### returned elements - this is probably when velocity is 0
        max_vel_bearing = grp['bearing'][grp['velocity'] == max_velocity].iloc[0]
        if max_vel_bearing >= 180:
            grp['wind_dir'] = max_vel_bearing - 180
        else:
            grp['wind_dir'] = max_vel_bearing + 180
            grp['wind_speed'] = max_velocity - 38
    except:
        grp['wind_dir'] = 0
        grp['wind_speed'] = 0
    return grp

###############################################################################
###############################################################################
### Function processes wind direction and speed
def process_wind(df):    
    ### add the wind direction and wind speed columns
    df['wind_dir'] = 0
    df['wind_speed'] = 0
    ### split apply combine at its finest:
    df = df.groupby(['flight_no', 'hour_minute']).apply(find_wind_dir_and_speed)
    return df

def wind_to_grid(df):
    ### clean up the grid numbers
    df['EW_grid'][df['EW_grid'] < 0] = 0
    df['EW_grid'][df['EW_grid'] > 9999] = 9999
    
    df['NS_grid'][df['NS_grid'] < 0] = 0
    df['NS_grid'][df['NS_grid'] > 9999] = 9999
    
    ### calculate mean wind speed
    summary = (df[df['circle'] == True].groupby(['date', 'hour', 'NS_grid', 'EW_grid'], as_index=False)
                 .agg({"wind_speed": [('_avg', lambda x:np.mean(x))]}))
    summary.columns = list(map(''.join,summary.columns.values))
    # merge wind speed with the original df database
    df = pd.merge(df, summary,
                            how='left', 
                            on=['date', 'hour', 'NS_grid', 'EW_grid'],
                            sort=False)
    
    ### calculate mean wind direction
    summary = (df[df['circle'] == True].groupby(['date', 'hour', 'NS_grid', 'EW_grid'], as_index=False)
                 .agg({"wind_dir": [('_avg', lambda x:np.mean(x))]}))
    summary.columns = list(map(''.join,summary.columns.values))
    # merge wind dir with the original df database
    df = pd.merge(df, summary,
                            how='left', 
                            on=['date', 'hour', 'NS_grid', 'EW_grid'],
                            sort=False)
    hour_of_day = df['hour'].unique()
    hour_of_day.sort()
    for hour in range(len(hour_of_day)):
        grid = np.zeros(shape = (10000, 10000))
        df_hour = df[df['hour'] == hour_of_day[hour]]
        try:
            grid[df_hour['NS_grid'], df_hour['EW_grid']] = df_hour['wind_dir_avg']
            array_name = "grid_wind_dir" + str(hour_of_day[hour])
            np.savez_compressed(path2data + folder_name + "\\" + array_name + ".npz", name = grid)
        except:
            pass
    return df

###############################################################################
### execution of the main part of the program #################################    
if __name__ == "__main__":

    ### setting up paths to various data files
    path2grid = 'D:\\Flights\\Grid\\'
    
#    # Slovakia
#    grid_folders = [path2grid + "N047E017\\", path2grid + "N047E018\\", path2grid + "N047E019\\",
#                    path2grid + "N047E020\\", path2grid + "N047E021\\",
#                    path2grid + "N048E017\\", path2grid + "N048E018\\", path2grid + "N048E019\\",
#                    path2grid + "N048E020\\", path2grid + "N048E021\\", path2grid + "N048E022\\",
#                    path2grid + "N049E017\\", path2grid + "N049E018\\", path2grid + "N049E019\\",
#                    path2grid + "N049E020\\", path2grid + "N049E021\\", path2grid + "N049E022\\"]

#    # Bassano    
#    grid_folders = [path2grid + "N045E011\\", path2grid + "N045E012\\", path2grid + "N045E013\\", path2grid + "N045E014\\",
#                    path2grid + "N046E011\\", path2grid + "N046E012\\", path2grid + "N046E013\\", path2grid + "N046E014\\"]

#    # Karkonosze
#    grid_folders = [path2grid + "N049E014\\", path2grid + "N049E015\\", path2grid + "N049E016\\",
#                    path2grid + "N049E017\\", path2grid + "N049E018\\",
#                    path2grid + "N050E014\\", path2grid + "N050E015\\", path2grid + "N050E016\\",
#                    path2grid + "N050E017\\", path2grid + "N050E018\\",
#                    path2grid + "N051E014\\", path2grid + "N051E015\\", path2grid + "N051E016\\",
#                    path2grid + "N051E017\\", path2grid + "N051E018\\"]
    
    # Perugia
    grid_folders = [path2grid + "N040E013\\", path2grid + "N040E014\\", path2grid + "N040E015\\",
                    path2grid + "N041E012\\", path2grid + "N041E013\\",
                    path2grid + "N041E014\\", path2grid + "N041E015\\",
                    path2grid + "N042E011\\", path2grid + "N042E012\\", path2grid + "N042E013\\",
                    path2grid + "N042E014\\",
                    path2grid + "N043E011\\", path2grid + "N043E012\\", path2grid + "N043E013\\",
                    path2grid + "N044E011\\", path2grid + "N044E012\\",
                    path2grid + "N044E014\\", path2grid + "N044E015\\"]

    ### calculate the minimum NS and EW to subtract to standardize the grid format
    min_NS, min_EW = min_grid(grid_folders)   
    for grid_folder in grid_folders:
        ### Measure time spent crunching each folder
        start_time = datetime.now()
        frame_file = grid_folder + "\\frame.csv"    
        ### read data from the data_frame saved in the folder
        df = pd.read_csv(frame_file, sep = ",")
        df = df.rename(columns = {'Unnamed: 0':'old_index'})
        df = df.drop(['old_index'], axis = 1)
        print(len(df['flight_no'].unique()))
        process_lift(df, grid_folder, min_NS, min_EW)
    
        ### print time spent crunching
        print(datetime.now() - start_time)
        ###process_sink_hours(df)
        ###df = process_circles(df)
        ###df = process_wind(df)
        ### processed all except wind
        ### df = wind_to_grid(df)
        ###df = process_lift_minutes(df)
        ### df.to_csv(frame_file, sep = ",")