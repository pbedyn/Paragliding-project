# -*- coding: utf-8 -*-
"""
Created on Thu Oct  4 18:35:53 2018
@author: Pawel Bedynski
"""

# TODO: Save flights that have not been scraped to a file for future reference
# TODO: Automatically discover how many flights are on the page and scrape all into a list
# TODO: Automatically detect the environment (lattepanda and my usual computer) and
#       automatically modify paths to folders and chromedrivers
# TODO: Determine length of the flight and scrape only those longer than e.g. 10km

# import standard Python libraries for execution
import os
import time
import pandas as pd
import numpy as np

# import warnings to suppress warnings during execution
import warnings
warnings.filterwarnings("ignore")


# set paths to a folder in Downloads where all tracks will be stored
# set to laptop as default, otherwise lattepanda, otherwise pawel
def set_paths():
    path2data = 'C:\\Users\\bedynskipa01\\Downloads\\flights\\'
    path2new_batch = 'C:\\Users\\bedynskipa01\\Downloads\\flights\\New Batch\\'
    path2drivers = 'C:\\Users\\bedynskipa01\\Downloads\\flights\\ChromeDrivers\\'
    path2tracks_file = 'C:\\Users\\bedynskipa01\\Downloads\\flights\\xc_tracks.csv'
    if not os.path.exists(path2data):
        path2data = 'C:\\Users\\LattePanda\\Downloads\\flights\\'
        path2new_batch = 'C:\\Users\\lattepanda\\Downloads\\flights\\New Batch\\'
        path2drivers = 'C:\\Users\\lattepanda\\Downloads\\flights\\ChromeDrivers\\'
        path2tracks_file = 'C:\\Users\\lattepanda\\Downloads\\flights\\xc_tracks.csv'
        if not os.path(path2data):
            path2data = 'C:\\Users\\pawel\\Downloads\\flights\\'
            path2new_batch = 'C:\\Users\\pawel\\Downloads\\flights\\New Batch\\'
            path2drivers = 'C:\\Users\\pawel\\Downloads\\flights\\ChromeDrivers\\'
            path2tracks_file = 'C:\\Users\\pawel\\Downloads\\flights\\xc_tracks.csv'
    return path2data, path2new_batch, path2drivers, path2tracks_file


# create a new directory
def create_folder(directory):
    try:
        if not os.path.exists(path2data + directory):
            os.makedirs(path2data + directory)
    except OSError:
        print("Error creating directory. " + directory)

# Identify digits in the string
def get_track_number(string):
    c = ""
    for i in string:
        if i.isdigit():
            c += i
    return c

# Identify digits in the string
def get_track_points(string):
    c = ""
    for i in string:
        if i.isdigit() or i == ".":
            c += i
    return c

# Identify digits in the string
def get_track_date(string):
    c = ""
    for i in string:
        if i.isdigit() or i == ".":
            c += i
    return c

# Create list of links
def create_list_links(path2data, longitude, latitude):        

    summary_file = str(longitude) + "_" + str(latitude) + ".txt"
    summary_file_path = path2data + summary_file
    
    # create a list of links to flights scraped to the file
    i = 0
    lines = []
    n_lines = 0
    L_tracks = []
    N_tracks = 0
    L_points = []
    L_dates = []
    with open(summary_file_path, 'r', encoding='utf-8') as f:
        for line in f:
            lines.append(line)
            n_lines += 1
            for word in line.split():
                if word.find('title="flight') == 0: # track found
                    N_tracks = N_tracks + 1
                    found = False
                    for word in line.split():
                        track = ''
                        # get track - word.find gives the position of the fragment in the string
                        if word.find('href="/world/en/flights/detail') == 0:
                            track = "https://www.xcontest.org/"
                            track = track + word[7:len(word) - 1]
                            #track = track.replace("/", "\\")
                        elif word.find('href="http://xc.dhv.de') == 0:
                            track = "https://www.dhv-xc.de/leonardo/index.php?op=show_flight&flightID="
                            track = track + get_track_number(word)
                        elif word.find('href="http://www.xc.dhv.de') == 0:
                            track = "https://www.dhv-xc.de/leonardo/index.php?op=show_flight&flightID="
                            track = track + get_track_number(word)
                        elif word.find('href="http://www.dhvxc.de') == 0:
                            track = "https://www.dhv-xc.de/leonardo/index.php?op=show_flight&flightID="
                            track = track + get_track_number(word)
                        elif word.find('href="http://www.paraglidingforum.com') == 0:
                            track = "http://www.paraglidingforum.com/modules.php?name=leonardo&op=show_flight&flightID="
                            track = track + get_track_number(word)
                        elif word.find('href="http://paraglidingforum.com') == 0:
                            track = "http://www.paraglidingforum.com/modules.php?name=leonardo&op=show_flight&flightID="
                            track = track + get_track_number(word)
                        elif word.find('href="http://www.sky.gr') == 0:
                            track = "http://www.sky.gr/leo/index.php?name=leonardo&op=show_flight&flightID="
                            track = track + get_track_number(word)
                        elif word.find('href="http://www.xcbrasil.org') == 0:
                            # might not work - site down
                            track = "http://www.xcbrasil.org/leonardo&op=show_flight&flightID="
                            track = track + get_track_number(word)
                        elif word.find('href="http://www.xcfc.de') == 0:
                            # might not work - site down
                            track = "http://www.xcfc.de/xc/modules.php?name=leonardo&op=show_flight&flightID="
                            track = track + get_track_number(word)
                        elif word.find('href="http://www.xcportugal.org') == 0:
                            # might not work - site down
                            track = "http://www.xcportugal.org/modules.php?name=leonardo&op=show_flight&flightID="
                            track = track + get_track_number(word)
                        elif word.find('href="http://www.ypforum.com') == 0:
                            # might not work - site down
                            track = "http://www.ypforum.com/leonardo&op=show_flight&flightID="
                            track = track + get_track_number(word)
                        elif word.find('href="http://dhvxc.dhv1.de') == 0:
                            # might not work - site down
                            track = "http://dhvxc.dhv1.de/phpBB/modules.php?name=leonardo&op=show_flight&flightID="
                            track = track + get_track_number(word)
                        elif word.find('href="http://www.xcaustralia.org') == 0:
                            # might not work - site down
                            track = "http://www.xcaustralia.org/modules.php?name=leonardo&op=show_flight&flightID="
                            track = track + get_track_number(word)
                        if track != '':
                            L_tracks.append(track)
                            i = i + 1
                            found = True
                    if found == True:
                        # get points - go back to three lines earlier and find points
                        points = ''
                        points_found = False
                        for track_word in lines[n_lines - 3].split():
                            if track_word.find('class="pts"><strong>') == 0:
                                points = get_track_points(track_word)
                                L_points.append(points)
                                points_found = True
                        if points_found == False:
                            L_points.append('')
                        # get date of the flight
                        date = lines[n_lines - 3][lines[n_lines - 3].find('title="submitted:') + 32: lines[n_lines - 3].find('title="submitted:') + 40]
                        if len(get_track_date(date)) == 8:
                            L_dates.append(date)
                        else:
                            L_dates.append('00.00.00')
                        ### if new type of track print it            
                    if found == False:
                        print(line)
    return L_tracks, L_points, L_dates

###############################################################################
# execution of the mian part of the program #################################
if __name__ == "__main__":

#    # set paths
#    path2data, path2new_batch, path2drivers, path2tracks_file = set_paths()
#    
#    non_scraped_file = "Non_scraped.txt"
#    non_scraped_file_path = path2data + non_scraped_file
    path2circles = "D:\\flights\\Circles\\East\\"
    
    L_tracks = []
    L_points = []
    L_dates = []
    
    for longitude in range(1, 27, 2):
        for latitude in range(35, 59, 2):
            try:
                new_L_tracks, new_L_points, new_L_dates = create_list_links(path2circles, longitude, latitude)
                L_tracks = L_tracks + new_L_tracks
                L_points = L_points + new_L_points
                L_dates = L_dates + new_L_dates
                print(longitude, latitude)
            except:
                pass
    
    df_tracks = pd.DataFrame()
    df_tracks['track'] = L_tracks
    df_tracks['points'] = L_points
    df_tracks['date'] = L_dates
    df_tracks['scraped'] = 0
    df_tracks = df_tracks.drop_duplicates(keep = 'first')
    
    
    # merge with the xc_tracks.csv database and update column 'scraped'
    xc_tracks = pd.read_csv("D:\\flights\\xc_tracks.csv", sep = ',')
    # rename "Unnamed: 0" column
    xc_tracks = xc_tracks.rename(columns={'Unnamed: 0': 'id'})
    # merge with df_tracks
    df_tracks = pd.merge(df_tracks, xc_tracks, on = 'track', how = 'left')
    df_tracks['scraped'][df_tracks['id'] < 25000] = 1
    df_tracks = df_tracks.drop(['id'], axis = 1)
    df_tracks = df_tracks[pd.to_numeric(df_tracks['points'], errors='coerce').notnull()]
    df_tracks['points'] = df_tracks['points'].astype(float)
    df_tracks = df_tracks.sort_values(by = ['points'], ascending = False)
    df_tracks.to_csv("D:\\flights\\df_tracks.csv")
    del new_L_tracks, new_L_points, new_L_dates, L_tracks, L_points, L_dates, xc_tracks