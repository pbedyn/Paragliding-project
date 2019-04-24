# -*- coding: utf-8 -*-
"""
Created on Fri Nov  2 18:27:15 2018
@author: Pawel Bedynski
Assumes there are npz numpy arrays that contain data for hours of day
Aggregates files for different hours and saves final outcome in the Hours folder
"""
from datetime import datetime
## packages to move files from one folder to another
import glob

### import pandas and numpy
import pandas as pd
import numpy as np

### import warnings to suppress warnings during execution
import warnings
warnings.filterwarnings("ignore")

### read lift.npz from all folders - done
### create one table containing all data by hour - done
### add lift from all folders by hour - done
### add a subset of hours (morning, afternoon) - TBD

### Grid problem
### read in all numpy arrays and sum up
### recalculate to coordinates - add min_NS, min_EW

### Determine the leftmost bottom corner of the grid
def min_grid(grid_folders):
    grid_NS = []
    grid_EW = []
    for grid_folder in grid_folders:
        grid_NS.append(int(grid_folder[len(grid_folder) - 8: len(grid_folder) - 5]))
        grid_EW.append(int(grid_folder[len(grid_folder) - 4: len(grid_folder) - 1]))
    return (min(grid_NS) - 1) * 1000, (min(grid_EW) - 1)* 1000


# createe one numpy array with one dimension for each grid
def create_sum_grid_array(grid_folders):
    colnumber = 0
    grid_array = np.zeros((len(grid_folders), 10000, 10000))
    for grid_folder in grid_folders:
        print(grid_folder)
        grid = grid_folder + "grid_lift.npz"
        ### extract the hour of the grid
        container = np.load(grid)
        array_to_add = container['name']
        grid_array[colnumber, :, :] = np.add(grid_array[colnumber, :, :], array_to_add)
        print(np.max(grid_array[colnumber::]))
        colnumber = colnumber + 1
    sum_grid_array = grid_array.sum(axis = 0)
    return sum_grid_array

###############################################################################        
### This function creates data_to_show.csv ready for visualizations
hour_array = np.zeros((12, 10000, 10000))
def create_hour_array(folder_name):
    source_files = path2grid + folder_name + "\\*.npz"
    filelist=glob.glob(source_files)
    ### 
    for file_ in filelist:
        ### extract the hour of the grid
        hour = file_[(len(file_) - 6):(len(file_) - 4)]
        container = np.load(file_)
        array_to_add = container['name']
        colnumber = int(hour) - 12
        hour_array[colnumber, :, :] = np.add(hour_array[colnumber, :, :], array_to_add)

### takes grid array and saves as dataframe of lift
def grid_data_to_show(sum_grid_array, path2grid, location_file_name):    
    ### Read in all grids from the folder
    data_to_show = pd.DataFrame()
    lon = []
    lat = []
    df = []
    
    for i in range(10000):
        for j in range(10000):
            lon.append((j + min_EW) / 1000.0)
            lat.append((i + min_NS) / 1000.0)
            df.append(sum_grid_array[i, j])

    for j in range(10000):
        for i in range(10000):
            lon.append((j + min_EW) / 1000.0)
            lat.append((i + min_NS) / 1000.0)
            df.append(sum_grid_array[i, j])
        
    lon_col = "lon"
    lat_col = "lat"
    data_col = "data"
    data_to_show[lon_col] = lon
    data_to_show[lat_col] = lat
    data_to_show[data_col] = df
    data_to_show.to_csv(path2grid + location_file_name + ".csv", sep = ",")


def save_hour_array(folder_name, a_type):
    for i in range(12):
        array_name = "grid_" + a_type + "_" + str(i + 12)
        np.save(path2grid + folder_name + "\\" + array_name + ".npy", hour_array[i, :, :])
        
def create_data_to_show(folder_name, a_type):    
    ### Read in all grids from the folder
    data_to_show = pd.DataFrame()
    if a_type == "sink" or a_type == "lift":
        for k in range(12):
            array_name = "grid_" + a_type + "_" + str(k + 12)
            grid = np.load(path2grid + folder_name + "\\" + array_name + ".npy")
            grid_sm = np.zeros((2000, 2000))
            lon = []
            lat = []
            df = []
        
            for i in range(2000):
                for j in range(2000):
                    grid_sm[i, j] = grid[i * 5, j * 5]
                    lon.append(74.4 + j * 5.0 / 5000.0)
                    lat.append(3.2 + i * 5.0 / 5000.0)
                    df.append(grid_sm[i, j])
        
            for j in range(2000):
                for i in range(2000):
                    grid_sm[i, j] = grid[i * 5, j * 5]
                    lon.append(74.4 + j * 5.0 / 5000.0)
                    lat.append(3.2 + i * 5.0 / 5000.0)
                    df.append(grid_sm[i, j])
                
            lon_col = "lon" + str(k + 12) 
            lat_col = "lat" + str(k + 12)   
            data_col = "data" + str(k + 12)
            data_to_show[lon_col] = lon
            data_to_show[lat_col] = lat
            data_to_show[data_col] = df
            
    else:
        array_name = "grid_" + a_type
        container = np.load(path2grid + folder_name + "\\" + array_name + ".npz")
        grid = container['name']
        grid_sm = np.zeros((2000, 2000))
        lon = []
        lat = []
        df = []
        
        for i in range(2000):
            for j in range(2000):
                grid_sm[i, j] = grid[i * 5, j * 5]
                lon.append(74.4 + j * 5.0 / 5000.0)
                lat.append(3.2 + i * 5.0 / 5000.0)
                df.append(grid_sm[i, j])
    
        for j in range(2000):
            for i in range(2000):
                grid_sm[i, j] = grid[i * 5, j * 5]
                lon.append(74.4 + j * 5.0 / 5000.0)
                lat.append(3.2 + i * 5.0 / 5000.0)
                df.append(grid_sm[i, j])
                
        lon_col = "lon" 
        lat_col = "lat"   
        data_col = "data"
        data_to_show[lon_col] = lon
        data_to_show[lat_col] = lat
        data_to_show[data_col] = df
    
    ### save the data_to_show file
    if a_type == "sink":
        data_to_show.to_csv(path2grid + folder_name + "\\" + "sink_data_to_show.csv", sep = ",")
    elif a_type == "lift":
        data_to_show.to_csv(path2grid + folder_name + "\\" + "lift_data_to_show.csv", sep = ",")
    else:
        data_to_show.to_csv(path2grid + folder_name + "\\" + "wind_data_to_show.csv", sep = ",")


def create_part_day_to_show(folder_name, a_type):    
    ### Read in all grids from the folder
    data_to_show = pd.DataFrame()
    array_name = "grid_" + a_type
    grid = np.load(path2grid + folder_name + "\\" + array_name + ".npy")
    grid_sm = np.zeros((2000, 2000))
    lon = []
    lat = []
    df = []

    for i in range(2000):
        for j in range(2000):
            grid_sm[i, j] = grid[i * 5, j * 5]
            lon.append(74.4 + j * 5.0 / 5000.0)
            lat.append(3.2 + i * 5.0 / 5000.0)
            df.append(grid_sm[i, j])

    for j in range(2000):
        for i in range(2000):
            grid_sm[i, j] = grid[i * 5, j * 5]
            lon.append(74.4 + j * 5.0 / 5000.0)
            lat.append(3.2 + i * 5.0 / 5000.0)
            df.append(grid_sm[i, j])
            
                
    lon_col = "lon" 
    lat_col = "lat"   
    data_col = "data"
    data_to_show[lon_col] = lon
    data_to_show[lat_col] = lat
    data_to_show[data_col] = df
    
    ### save the data_to_show file
    if a_type == "sink":
        data_to_show.to_csv(path2grid + folder_name + "\\" + "sink_data_to_show.csv", sep = ",")
    elif a_type == "lift":
        data_to_show.to_csv(path2grid + folder_name + "\\" + "lift_data_to_show.csv", sep = ",")
    else:
        data_to_show.to_csv(path2grid + folder_name + "\\" + "wind_data_to_show.csv", sep = ",")


#### Create data for xgboost model
def create_data_for_model(folder_name, size, a_type):    
    ### Read in all grids from the folder
    data_to_show = pd.DataFrame()
    if a_type == "sink" or a_type == "lift":
        for k in range(12):
            array_name = "grid_" + a_type + "_" + str(k + 12)
            grid = np.load(path2grid + folder_name + "\\" + array_name + ".npy")
            grid_sm = np.zeros((size, size))
            lon = []
            lat = []
            data = []
            data_01, data_02, data_03, data_04, data_05, data_06, data_07, data_08 = [], [], [], [], [], [], [], []
        
            for i in range(1, size - 1):
                for j in range(1, size - 1):
                    grid_sm[i, j] = grid[int(i * 10000 / size), int(j * 10000 / size)]
                    lon.append(74.4 + j / 1000.0)
                    lat.append(3.2 + i / 1000.0)
                    data.append(grid_sm[i, j])
                    data_01.append(grid_sm[i - 1, j - 1])
                    data_02.append(grid_sm[i - 1, j])
                    data_03.append(grid_sm[i - 1, j + 1])
                    data_04.append(grid_sm[i, j - 1])
                    data_05.append(grid_sm[i, j + 1])
                    data_06.append(grid_sm[i + 1, j - 1])
                    data_07.append(grid_sm[i + 1, j])
                    data_08.append(grid_sm[i + 1, j + 1])
            
            if k == 0:
                lon_col = "lon"
                lat_col = "lat"
                data_to_show[lon_col] = lon
                data_to_show[lat_col] = lat
            data_col = "data_" + str(k)
            data_to_show[data_col] = data
            data_col = "data_" + str(k) + "_01"
            data_to_show[data_col] = data_01
            data_col = "data_" + str(k) + "_02"
            data_to_show[data_col] = data_02
            data_col = "data_" + str(k) + "_03"
            data_to_show[data_col] = data_03
            data_col = "data_" + str(k) + "_04"
            data_to_show[data_col] = data_04
            data_col = "data_" + str(k) + "_05"
            data_to_show[data_col] = data_05
            data_col = "data_" + str(k) + "_06"
            data_to_show[data_col] = data_06
            data_col = "data_" + str(k) + "_07"
            data_to_show[data_col] = data_07
            data_col = "data_" + str(k) + "_08"
            data_to_show[data_col] = data_08
            
    else:
        array_name = "grid_" + a_type
        container = np.load(path2grid + folder_name + "\\" + array_name + ".npz")
        grid = container['name']
        grid_sm = np.zeros((size, size))
        lon = []
        lat = []
        data_01, data_02, data_03, data_04, data_05, data_06, data_07, data_08 = [], [], [], [], [], [], [], []

        
        for i in range(1, size - 1):
            for j in range(1, size - 1):
                grid_sm[i, j] = grid[int(i * 10000 / size), int(j * 10000 / size)]
                lon.append(74.4 + j / 1000.0)
                lat.append(3.2 + i / 1000.0)
                data.append(grid_sm[i, j])
                data_01.append(grid_sm[i - 1, j - 1])
                data_02.append(grid_sm[i - 1, j])
                data_03.append(grid_sm[i - 1, j + 1])
                data_04.append(grid_sm[i, j - 1])
                data_05.append(grid_sm[i, j + 1])
                data_06.append(grid_sm[i + 1, j - 1])
                data_07.append(grid_sm[i + 1, j])
                data_08.append(grid_sm[i + 1, j + 1])
                
            if k == 0:
                lon_col = "lon"
                lat_col = "lat"
                data_to_show[lon_col] = lon
                data_to_show[lat_col] = lat
            data_col = "data_" + str(k)
            data_to_show[data_col] = data
            data_col = "data_" + str(k) + "_01"
            data_to_show[data_col] = data_01
            data_col = "data_" + str(k) + "_02"
            data_to_show[data_col] = data_02
            data_col = "data_" + str(k) + "_03"
            data_to_show[data_col] = data_03
            data_col = "data_" + str(k) + "_04"
            data_to_show[data_col] = data_04
            data_col = "data_" + str(k) + "_05"
            data_to_show[data_col] = data_05
            data_col = "data_" + str(k) + "_06"
            data_to_show[data_col] = data_06
            data_col = "data_" + str(k) + "_07"
            data_to_show[data_col] = data_07
            data_col = "data_" + str(k) + "_08"
            data_to_show[data_col] = data_08
    
    ### save the data_to_show file
    if a_type == "sink":
        data_to_show.to_csv(path2grid + folder_name + "\\" + "sink_data_to_model.csv", sep = ",")
    elif a_type == "lift":
        data_to_show.to_csv(path2grid + folder_name + "\\" + "lift_data_to_model.csv", sep = ",")
    else:
        data_to_show.to_csv(path2grid + folder_name + "\\" + "wind_data_to_model.csv", sep = ",")


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

    
    start_time = datetime.now()
    ### calculate the minimum NS and EW to subtract to standardize the grid format
    min_NS, min_EW = min_grid(grid_folders)
    # create sum_grid_array with data for each grid in a different dimension
    sum_grid_array = create_sum_grid_array(grid_folders)
    # create data to show .csv containing thermal grid for the location
    location_file_name = "Karkonosze"
    grid_data_to_show(sum_grid_array, path2grid, location_file_name)
    
    print(datetime.now() - start_time)