# -*- coding: utf-8 -*-
"""
Created on Sat Oct 20 09:12:00 2018
@author: Pawel Bedynski
Go through all folders within a given grid
Read in all files and create one dataframe within each grid
Assumes there are new igc files in the folder or the folder needs preprocessing
Takes all igc files in the folder and imports them into a dataframe
Saves the dataframe into the "frame" file in that grid folder
"""
from datetime import datetime
# packages to move files from one folder to another
import glob
import zipfile
import os
from os.path import basename

# import pandas and numpy
import pandas as pd
import numpy as np

# import warnings to suppress warnings during execution
import warnings
warnings.filterwarnings("ignore")

# setting up paths to various data files
path2grid = 'D:\\Flights\\Grid\\'


###############################################################################
# This function takes grid folder, walks through all folders within the grid
# and precomputes files raw_data_file (all raw) and frame within the grid folder
def preprocess_grid(grid_folder):
    
    # create a list of folders within the grid
    subfolders = [f.path for f in os.scandir(grid_folder) if f.is_dir()]
    raw_track_data = pd.DataFrame()
    list_ = []
    flight_no = 0    
    
    for subfolder in subfolders: 
        allFiles = glob.glob(subfolder + "\\" + "*.igc")
        for single_file in allFiles:
            flight_no += 1
            try:
                df = pd.read_csv(single_file, index_col = None, header=None, skiprows = 0, usecols=[0], encoding = "ISO-8859-1")
                df.columns = ["record"]
                df["date"] = df['record'][min(df[df["record"].str.startswith("HFDTE") == True].index.tolist())]
                df["flight_no"] = flight_no
                list_.append(df)
            except:
                pass
    print(flight_no)
    
    raw_track_data = pd.concat(list_, sort = False)
    # drop duplicates (files are extracted from different sites - there may
    # still be duplicates)
    raw_track_data = raw_track_data.drop_duplicates(subset=['record', 'date'], keep="first")
    
    # clean up after processing
    del single_file, list_, df
    
    # save the raw track data file
    raw_track_file = grid_folder + "raw_track_file.csv"
    raw_track_data.to_csv(raw_track_file, sep = "\t")
    
    # extracts only flight records starting with a "B"
    df = raw_track_data[raw_track_data["record"].str.startswith("B") == True]    
    
    # saves dataframe as Series
    my_series = df["record"].T.squeeze()
    # extract data from the series to represent the different data facts
    df["flight_time"] = my_series.str.slice(1, 7, 1)
    df["latitude"] = my_series.str.slice(7, 14, 1)
    df["lat_orient"] = my_series.str.slice(14, 15, 1)
    df["longitude"] = my_series.str.slice(15, 23, 1)
    df["lon_orient"] = my_series.str.slice(23, 24, 1)
    df["bar_alt"] = my_series.str.slice(25, 30, 1)
    df["gps_alt"] = my_series.str.slice(31, 35, 1)
    
    del my_series
    
    # extract only numeric data from the data field (eliminate the "HFDTE" and the such)
    # df column needs to be transposed into a series in order to perform this operation
    df['date'] = df['date'].T.squeeze().str.extract('(\d\d\d\d\d\d)', expand = True)
    # change format of the date field to yymmdd
    df['date'] = df['date'].str.slice(4, 6, 1) + \
                   df['date'].str.slice(2, 4, 1) + \
                   df['date'].str.slice(0, 2, 1)
                     
    # delete rogue records after conversion of latitude and longitude
    df['longitude'] = df['longitude'].str.replace('-','0')
    df = df[pd.to_numeric(df['longitude'], errors='coerce').notnull()]
    df = df[pd.to_numeric(df['latitude'], errors='coerce').notnull()]

    # convert longitude and latitude to float and recalculate into decimal degrees
    df['longitude'] = df['longitude'].astype(float)
    df['longitude'] = df['longitude'] / 100000.0
    # convert longitude to decimal degrees
    df['longitude'] = np.modf(df['longitude'])[1] + np.modf(df['longitude'])[0] / 0.6
    
    df['latitude'] = df['latitude'].astype(float)
    df['latitude'] = df['latitude'] / 100000.0
    # convert latitude to decimal degrees
    df['latitude'] = np.modf(df['latitude'])[1] + np.modf(df['latitude'])[0] / 0.6
    
    ###########################################################################
    # Add a function that assigns NS_sm_grid and EW_sm_grid
    # NS are rows in the numpy array, EW are columns
    # This will be important for crating grids
    df['NS_grid'] = (round(1000 * (df['latitude']), 0)).astype(int)
    df['EW_grid'] = (round(1000 * (df['longitude']), 0)).astype(int)

    # time will depend on the time zone so needs to be addressed further
    # clean up the time column - if time greater than 235959 drop the row
    df = df[df['flight_time'] < "235959"]
    df = df[df['flight_time'] > "000000"]
    df['hour'] = df['flight_time'].str.slice(0, 2, 1)
    df['minute'] = df['flight_time'].str.slice(2, 4, 1)
    df['hour_minute'] = df['flight_time'].str.slice(0, 4, 1)
    df['second'] = df['flight_time'].str.slice(4, 6, 1)
    
    # clean up the flight_time column
    # if seconds == 60 delete the record
    # if seconds > 60 delete the entire flight
    df = df[df['second'] != '60']
    corrupt_flights = df['flight_no'][df['second'] > '59'].to_frame()
    df = df.loc[~df['flight_no'].isin(corrupt_flights['flight_no']), :]
    
    # prepare the time_diff column
    df['flight_time_shifted'] = df['flight_time'].shift(1)
    df['flight_time_shifted'][df['flight_time_shifted'].isnull()] = df['flight_time']
        
    df['time_diff'] = df['flight_time'].apply(lambda x: datetime.strptime(x, '%H%M%S')) - \
                            df['flight_time_shifted'].apply(lambda x: datetime.strptime(x, '%H%M%S'))
                            
    df['time_diff'] = df['time_diff'].apply(lambda x: x.total_seconds())    
    df['time_diff'][df['time_diff'] == 0] = 1.0
    # drop the auxiliary flight_time_shifted column
    df = df.drop(['flight_time_shifted'], axis = 1)
    
    # run calculation funtions
    df['distance'] = calc_distance(df)
    # clean up the calculcated distance
    df['distance'][df['distance'] > 1] = 0
    df['bearing'] = calc_bearing(df)
    df['velocity'] = calc_velocity(df)
    
    df['bar_alt'] = df['bar_alt'].apply(lambda x: float(x) if x.isnumeric() else 0)
    df['bar_alt_diff'] = calc_height_gain(df, "bar_alt")
    
    df['gps_alt'] = df['gps_alt'].apply(lambda x: float(x) if x.isnumeric() else 0)
    df['gps_alt_diff'] = calc_height_gain(df, "gps_alt")
    df['bar_alt_vel'] = inst_vel_m_per_s(df['bar_alt_diff'], df['time_diff'])
    df['gps_alt_vel'] = inst_vel_m_per_s(df['gps_alt_diff'], df['time_diff'])
    
    ###############################################################################
    
    df = df.drop(['bar_alt_shifted'], axis = 1)
    df = df.drop(['gps_alt_shifted'], axis = 1)
    
    # run some basics statistics to check if everything worked out fine
    print("velocity", min(df['velocity']), max(df['velocity']))
    print("bearing", min(df['bearing']), max(df['bearing']))
    print("gps_alt_vel", min(df['gps_alt_vel']), max(df['gps_alt_vel']))
    
    # Save the data with different calculated columns to Archives
    frame_file = grid_folder + "frame.csv"
    df.to_csv(frame_file, sep = ",")
    
    # delete components that went into building the df test data frame
    del allFiles, raw_track_file, raw_track_data, frame_file, df


###############################################################################
# Before processing files we need to extract old from the zip file to make
# sure we don't create duplicates we can't handle
def read_zip_igcs(folder_name):
    archive = zipfile.ZipFile(path2grid + folder_name + "\\zip_igcs.zip", "r")
    archive.extractall(path2grid + folder_name)
    archive.close()
    os.remove(path2grid + folder_name + "\\zip_igcs.zip")


###############################################################################
# Zip the igc_files - saves a lot of space
def save_zip_igcs(folder_name):
    source_files = folder_name + "\\*.igc"
    # if the zip file exists remove it
    if os.path.exists(folder_name + "\\zip_igcs.zip"):
        os.remove(folder_name + "\\zip_igcs.zip")
    zip_file = zipfile.ZipFile(folder_name + "\\zip_igcs.zip", "x", zipfile.ZIP_DEFLATED)
    filelist=glob.glob(source_files)
    # move all igc files to a separate folder for zipping
    for file in filelist:
        # zip the files
        zip_file.write(file, basename(file))
        os.remove(file)
    zip_file.close()

###############################################################################
###############################################################################
# END OF THE PREPROCESSING FUNCTION

## Slovakia
#grid_folders = [path2grid + "N047E017\\", path2grid + "N047E018\\", path2grid + "N047E019\\",
#                path2grid + "N047E020\\", path2grid + "N047E021\\",
#                path2grid + "N048E017\\", path2grid + "N048E018\\", path2grid + "N048E019\\",
#                path2grid + "N048E020\\", path2grid + "N048E021\\", path2grid + "N048E022\\",
#                path2grid + "N049E017\\", path2grid + "N049E018\\", path2grid + "N049E019\\",
#                path2grid + "N049E020\\", path2grid + "N049E021\\", path2grid + "N049E022\\"]

# Bassano    
#grid_folders = [path2grid + "N045E011\\", path2grid + "N045E012\\", path2grid + "N045E013\\", path2grid + "N045E014\\",
#                path2grid + "N046E011\\", path2grid + "N046E012\\", path2grid + "N046E013\\", path2grid + "N046E014\\"]

# Karkonosze
grid_folders = [path2grid + "N049E014\\", path2grid + "N049E015\\", path2grid + "N049E016\\",
                path2grid + "N049E017\\", path2grid + "N049E018\\",
                path2grid + "N050E014\\", path2grid + "N050E015\\", path2grid + "N050E016\\",
                path2grid + "N050E017\\", path2grid + "N050E018\\",
                path2grid + "N051E014\\", path2grid + "N051E015\\", path2grid + "N051E016\\",
                path2grid + "N051E017\\", path2grid + "N051E018\\"]

## Perugia
#grid_folders = [path2grid + "N040E013\\", path2grid + "N040E014\\", path2grid + "N040E015\\",
#                path2grid + "N041E012\\", path2grid + "N041E013\\",
#                path2grid + "N041E014\\", path2grid + "N041E015\\",
#                path2grid + "N042E011\\", path2grid + "N042E012\\", path2grid + "N042E013\\",
#                path2grid + "N042E014\\",
#                path2grid + "N043E011\\", path2grid + "N043E012\\", path2grid + "N043E013\\",
#                path2grid + "N044E011\\", path2grid + "N044E012\\",
#                path2grid + "N044E014\\", path2grid + "N044E015\\"]

# St_Andres
#grid_folders = [path2grid + "N043E005\\", path2grid + "N043E006\\", path2grid + "N043E007\\",
#                path2grid + "N044E005\\", path2grid + "N044E006\\",
#                path2grid + "N045E005\\", path2grid + "N045E006\\", path2grid + "N045E007\\",
#                path2grid + "N045E008\\"]
                
for grid_folder in grid_folders:
    start_time = datetime.now()
    print(grid_folder)
    preprocess_grid(grid_folder)
    # print time spent crunching
    print(datetime.now() - start_time)