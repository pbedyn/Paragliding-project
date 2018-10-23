# -*- coding: utf-8 -*-
"""
Created on Sat Oct 20 09:12:00 2018

@author: BedynskiPa01
"""
from datetime import datetime
## packages to move files from one folder to another
import glob
import shutil

### import pandas and numpy
import pandas as pd
import numpy as np

### import warnings to suppress warnings during execution
import warnings
warnings.filterwarnings("ignore")

### we'll measure performance of this little beauty
start_time = datetime.now()

### working with data
path2data = 'C:\\Users\\bedynskipa01\\Downloads\\Flights\\'
###path2data = 'C:\\Users\\bedynskipa01\\Downloads\\Flights_example\\'
allFiles = glob.glob(path2data + "*.igc")
frame = pd.DataFrame()
list_ = []
summary_list = []
for single_file in allFiles:
    single_file_adj = single_file[0:len(single_file) - 4] + ".csv"
    shutil.move(single_file, single_file_adj)
    try:
        df = pd.read_csv(single_file_adj, index_col = None, header=None, skiprows = 0, usecols=[0], encoding = "ISO-8859-1")
        df.columns = ["record"]
        ### the list summary_list contains flight statistics and reference to the file
        ### it is reshaped later to a 4 column data frame called "summary_df"
        summary_list.append(single_file)
        summary_list.append(df['record'][min(df[df["record"].str.startswith("HFDTE") == True].index.tolist())])
        summary_list.append(df['record'][min(df[df["record"].str.startswith("B") == True].index.tolist())])
        summary_list.append(df['record'][max(df[df["record"].str.startswith("B") == True].index.tolist())])
        summary_list.append(min(df[df["record"].str.startswith("B") == True].index.tolist()))
        summary_list.append(max(df[df["record"].str.startswith("B") == True].index.tolist()))
        df["date"] = df['record'][min(df[df["record"].str.startswith("HFDTE") == True].index.tolist())]
        list_.append(df)
    except:
        pass
    shutil.move(single_file_adj, single_file)
frame = pd.concat(list_, sort = False)
### drop duplicates
frame = frame.drop_duplicates(subset=['record', 'date'], keep="first")

### reshape the summary_list into the 4 column data frame summary_df
colnames = ['flight_file', 'date', 'start_record', 'finish_record', 'start_position', 'finish_position']
summary_df = pd.DataFrame(np.array(summary_list).reshape(-1, len(colnames)), columns = colnames)
del single_file, single_file_adj, colnames, summary_list, list_, df

frame = frame.drop_duplicates(subset=['record', 'date'], keep="first")
## extracts only flight records starting with a "B"
df_t = frame[frame["record"].str.startswith("B") == True]    

### saves dataframe as Series
my_series = df_t["record"].T.squeeze()
### extract data from the series to represent the different data facts
df_t["flight_time"] = my_series.str.slice(1, 7, 1)
df_t["latitude"] = my_series.str.slice(7, 14, 1)
df_t["lat_orient"] = my_series.str.slice(14, 15, 1)
df_t["longitude"] = my_series.str.slice(15, 23, 1)
df_t["lon_orient"] = my_series.str.slice(23, 24, 1)
df_t["bar_alt"] = my_series.str.slice(25, 30, 1)
df_t["gps_alt"] = my_series.str.slice(31, 35, 1)

### extract only numeric data from the data field (eliminate the "HFDTE" and the such)
### df_t column needs to be transposed into a series in order to perform this operation
df_t['date'] = df_t['date'].T.squeeze().str.extract('(\d\d\d\d\d\d)', expand = True)
### change format of the date field to yymmdd
df_t['date'] = df_t['date'].str.slice(4, 6, 1) + \
               df_t['date'].str.slice(2, 4, 1) + \
               df_t['date'].str.slice(0, 2, 1)
frame_file = path2data + "frame_test.csv"
df_t.to_csv(frame_file, sep = ",")
## df_t = pd.read_csv(frame_file, index_col = 0)

series_file = path2data + "my_series.csv"
my_series.to_csv(series_file, sep = ",")
## my_series = pd.read_csv(series_file, header = -1, index_col = 0)
## my_series = my_series.T.squeeze()

## delete components that went into building the df_t test data frame
del allFiles, frame_file, series_file, my_series

df_t['longitude'] = df_t['longitude'].str.replace('-','0')
df_t['longitude'] = df_t['longitude'].astype(float)
df_t['longitude'] = df_t['longitude'] / 100000.0

df_t['latitude'] = df_t['latitude'].astype(float)
df_t['latitude'] = df_t['latitude'] / 100000.0
df_t['latitude'][df_t['latitude'] > 10.0] = df_t['latitude'] / 10.0

## prepare the time_diff column
df_t['flight_time'] = df_t['flight_time'].astype(float)
df_t['flight_time_shifted'] = df_t['flight_time'].shift(1)
df_t['flight_time_shifted'][df_t['flight_time_shifted'].isnull()] = df_t['flight_time']
df_t['time_diff'] = df_t['flight_time'] - df_t['flight_time_shifted']
df_t['time_diff'][df_t['time_diff'] == 0] = 1.0
## drop the auxiliary flight_time_shifted column
df_t = df_t.drop(['flight_time_shifted'], axis = 1)

## run calculation funtions
df_t['distance'] = calc_distance(df_t)
## clean up the calculcated distance
df_t['distance'][df_t['distance'] > 1] = 0
df_t['bearing'] = calc_bearing(df_t)
df_t['velocity'] = calc_velocity(df_t)

df_t['bar_alt'] = df_t['bar_alt'].astype(float)
df_t['bar_alt_diff'] = calc_height_gain(df_t, "bar_alt")

df_t['gps_alt'] = df_t['gps_alt'].astype(float)
df_t['gps_alt_diff'] = calc_height_gain(df_t, "gps_alt")
df_t['bar_alt_vel'] = inst_vel_m_per_s(df_t['bar_alt_diff'], df_t['time_diff'])
df_t['gps_alt_vel'] = inst_vel_m_per_s(df_t['gps_alt_diff'], df_t['time_diff'])

###############################################################################
#### clean up the data frame 
df_t['velocity'][df_t['velocity'] > 100] = 0
df_t['velocity'][df_t['velocity'] < 0] = 0

df_t = df_t.drop(['bar_alt_shifted'], axis = 1)
df_t = df_t.drop(['gps_alt_shifted'], axis = 1)

## run some basics statistics to check if everything worked out fine
print("velocity", min(df_t['velocity']), max(df_t['velocity']))
print("bearing", min(df_t['bearing']), max(df_t['bearing']))
print("gps_alt_vel", min(df_t['gps_alt_vel']), max(df_t['gps_alt_vel']))

### print time spent crunching
print(datetime.now() - start_time)

### deduplicate the summary_df and extract numeric date
summary_df = summary_df.drop_duplicates(subset=['date', 'start_record', 'finish_record'], keep="first")
summary_df_date = summary_df['date'].T.squeeze()
summary_df['date'] = summary_df_date.str.extract('(\d\d\d\d\d\d)', expand = True)
summary_df['date'] = summary_df['date'].str.slice(4, 6, 1) + \
                     summary_df['date'].str.slice(2, 4, 1) + \
                     summary_df['date'].str.slice(0, 2, 1)
del summary_df_date

days = pd.DataFrame()
days['sum_distance'] = df_t['distance'].groupby(df_t["date"]).sum()

### take the numeric summary of flights from summary_df
num_flights = summary_df['date'].groupby(summary_df["date"]).count().to_frame()
### merge the distance summary with numeric number of flights
days = pd.merge(days, num_flights, left_index = True, right_index = True)

### Create a grid of one 10000ths of a decimal degree as the playground to store
### information about thermals
start_time = datetime.now()
grid = np.zeros(shape = (20000, 20000))
longitude = df_t['longitude']
latitude = df_t['latitude']
gps_alt_diff = df_t['gps_alt_diff']
###for i in range(1000):
for i in range(len(longitude)):
    column = 20000 - int(round(10000 * (77.0 - longitude.values[i]), 0))
    row = 20000 - int(round(10000 * (5.4 - latitude.values[i]), 0))
    if (0 <= column < 20000) and (0 <= row < 20000):
        if gps_alt_diff.values[i] > 0:
            for j in range(-3, 4):
                for k in range(-3, 4):
                    grid[row + j, column + k] = grid[row + j, column + k] + gps_alt_diff.values[i]

### print time spent crunching
print(datetime.now() - start_time)

sum_grid_columns = np.sum(grid, axis = 0)
sum_grid_rows = np.sum(grid, axis = 1)
import matplotlib.pyplot as plt
plt.plot(sum_grid_columns)
plt.plot(sum_grid_rows)
np.amax(grid)

small_grid = grid[0:3000, 0:3000]
np.amax(small_grid)
np.unravel_index(np.argmax(grid, axis=None), grid.shape)
