# -*- coding: utf-8 -*-
"""
Created on Thu Mar  7 22:18:17 2019
@author: BedynskiPa01
"""
###############################################################################
# Reads igc files from New Batch folder (new igc files have to be manually copied there)
# If name of the file contains non-ASCII characters modify the name
###############################################################################
# Reads in the first B record specifying the start location of the flight
# Based on first B record check if flight in the repository, if yes, delete the new file else continue
###############################################################################
# If grid folder with coordinates of that start location exists place file in that folder
# If grid folder does not exist create a new folder
###############################################################################
# Read in the date of the flight, place it in the month folder based on the date
# If folder month year folder does not exist create the folder
# Move file to the month year folder within the right grid
###############################################################################
# The repo file is 'D:\\Flights\\Grid\\flight_repo.txt'

# import standard Python libraries for manipulation of files and folders
import glob
import shutil
import os

# import data manipulation libraries
import pandas as pd

###############################################################################
# igc file class - not finished yet
class IgcFile():
    # initialize the class
    def __init__(self, path2file):
        self.path2file = path2file
    
    # check if the file exists
    def file_exists(self):
        try:
            if os.path.exists(self.path2file):
                return True
            else:
                return False
        except OSError:
            print("Error verifying file existence " + self.path2file)
    
    ###############################################################################
    # Function moves a file to a specified folder
    def move_file(self, target_folder):
        # move file with full paths as shutil.move() parameters
        try:
            shutil.move(self.path2file, target_folder)
        except:
            i = 0
            file_moved = False
            # if file with the same name exists, change name before moving
            while file_moved == False:
                source_file_adj = self.path2file[0:len(self.path2file) - 4] + "_" + str(i) + ".igc"
                shutil.move(self.path2file, source_file_adj)
                try:
                    shutil.move(source_file_adj, target_folder)
                    file_moved = True
                except:
                    pass
                i = i + 1
                self.path2file = source_file_adj

###############################################################################
# Set path to a folder in Downloads where all tracks will be stored
def set_paths():
    path2data = 'D:\\Flights\\Grid\\'
    path2_new_files = 'D:\\Flights\\New Batch\\'
    duplicated_folder = 'D:\\Flights\\Duplicated flights\\'
    return path2data, path2_new_files, duplicated_folder

###############################################################################
# Function creating a new folder
def create_folder(path2data, directory):
    try:
        if not os.path.exists(path2data + directory):
            os.makedirs(path2data + directory)
    except OSError:
        print("Error creating directory " + directory)

###############################################################################
# Function checking whether a fileor folder exists
def check_file_folder_exists(path2filefolder):
    try:
        if os.path.exists(path2filefolder):
            return True
        else:
            return False
    except OSError:
        print("Error verifying file existence " + path2filefolder)

###############################################################################
# Function checks if track exists in the repository based on the first B record
def check_track_exists(source_file, flight_repo):
    # Returns True/False, grid_folder, month_folder, b_record
    try:
        df = pd.read_csv(source_file, index_col = None, header = None, skiprows = 0, usecols=[0], encoding="ISO-8859-1")
        df.columns = ["record"]
        #######################################################################
        # Files are saved based on month and year extracted from the track
        date_entry = df[df['record'].str.startswith("HFDTE") == True].iloc[0].item()
        # strip tab characters
        date_entry = date_entry.strip('\t')
        month = date_entry[len(date_entry) - 4:len(date_entry) - 2]
        year = date_entry[len(date_entry) - 2:len(date_entry)]

        #######################################################################
        # extract first b record from the file
        # extract latitude, lat_orient, longitude, lon_orient for the grid
        b_record_entry = df[df["record"].str.startswith("B") == True].iloc[0].item()
        latitude = b_record_entry[7:14]
        lat_orient = b_record_entry[14:15]
        longitude = b_record_entry[15:23]
        lon_orient = b_record_entry[23:24]
        
        #######################################################################
        # determine destination folder to save the file in
        grid_folder = lat_orient + "0" + str(latitude)[0:2] + lon_orient + str(longitude)[0:3]
        # determine the month folder to save the file in
        month_folder = year + month
        
        #######################################################################
        # check if file exists
        if len(flight_repo) > 0:
            if b_record_entry in flight_repo["record"].tolist():
                return True, grid_folder, month_folder, b_record_entry
            else:
                return False, grid_folder, month_folder, b_record_entry
        else:
            return False, grid_folder, month_folder, b_record_entry
    except:
        print("Error occurred while manipulating the igc file", source_file)

###############################################################################
# Function deletes non_ascii characters from the name of the file
def delete_non_ascii(single_file):
    for c in single_file:
        if 0 <= ord(c) <= 127:
            pass
        else:
            char_to_del = single_file.find(c)
            single_file = single_file[0:char_to_del] + single_file[char_to_del + 1:len(single_file)]
    return single_file

###############################################################################
# Function moves a file to a specified folder
def move_file(source_file, target_folder):
    # move files to the destination folder
    # retrieve file list
    # move file with full paths as shutil.move() parameters
    try:
        shutil.move(source_file, target_folder)
    except:
        i = 0
        file_moved = False
        while file_moved == False:
            source_file_adj = source_file[0:len(source_file) - 4] + "_" + str(i) + ".igc"
            shutil.move(source_file, source_file_adj)
            try:
                shutil.move(source_file_adj, target_folder)
                file_moved = True
            except:
                pass
            i = i + 1
            source_file = source_file_adj

# Move files from the New Batch folder to the grid
def move_new_files_to_grid(path2_new_files, flight_repo_file):
    # create list of all .igc files inside the New Batch folder
    allFiles = glob.glob(path2_new_files + "*.igc")
    flight_repo = pd.read_csv(flight_repo_file, index_col = None, header = None, skiprows = 0, usecols=[0], encoding = "ISO-8859-1")
    flight_repo.columns = ["record"]    
    for single_file in allFiles:
        # delete non-ascii characters from the name of the file
        shutil.move(single_file, delete_non_ascii(single_file))
        single_file = delete_non_ascii(single_file)
        flight_exists, destination_folder, month_folder, b_record_entry = check_track_exists(single_file, flight_repo)
        if flight_exists == False:
            if check_file_folder_exists(path2grids + destination_folder + "\\" + month_folder) == False:
                create_folder(path2grids, destination_folder + "\\" + month_folder)
            move_file(single_file, path2grids + destination_folder + "\\" + month_folder + "\\")
            with open(flight_repo_file, 'a', encoding='utf-8') as the_file:
                the_file.write(b_record_entry + "\n")
            flight_repo = flight_repo.append({'record': b_record_entry}, ignore_index = True)
        else:
            print("flight exists; moved to the Duplicated flights folder")
            move_file(single_file, duplicated_folder)    

###############################################################################
# execution of the main part of the program ###################################
if __name__ == "__main__":

    # set paths
    path2grids, path2_new_files, duplicated_folder = set_paths()
    # point to the repository file
    flight_repo_file = path2grids + '\\flight_repo.txt'
    # move files from New Batch to Grid
    move_new_files_to_grid(path2_new_files, flight_repo_file)
