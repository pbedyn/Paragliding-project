# -*- coding: utf-8 -*-
"""
Created on Sat Apr 13 10:00:21 2019

@author: pawel
"""
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
import pandas as pd
from random import randint

### import webscraping libraries
from selenium import webdriver

### import win modules for scraping the dhv site
import win32api, win32con, win32gui

### set path to a folder in Downloads where all tracks will be stored
def set_paths():
    path2data = 'C:\\Users\\pawel\\Downloads\\flights\\'
    path2file = 'C:\\Users\\pawel\\Downloads\\flights\\New Batch\\'
    path2drivers = "C:\\Users\\pawel\\Downloads\\flights\\ChromeDrivers\\"    
    if not os.path.exists(path2data):
        path2data = 'C:\\Users\\lattepanda\\Downloads\\flights\\'    
        path2file = 'C:\\Users\\lattepanda\\Downloads\\flights\\Poland\\New Batch\\'
        path2drivers = "C:\\Users\\lattepanda\\Downloads\\flights\\ChromeDrivers\\"
    return path2data, path2file, path2drivers

# click mouse at a given location
def mouse_click(x,y):
    win32api.SetCursorPos((x,y))
    win32api.mouse_event(win32con.MOUSEEVENTF_LEFTDOWN, x, y, 0, 0)
    win32api.mouse_event(win32con.MOUSEEVENTF_LEFTUP, x, y, 0, 0)    ### set paths
    
###############################################################################
### execution of the mian part of the program #################################    
if __name__ == "__main__":
    
    path2data, path2file, path2drivers = set_paths()
    
    non_scraped_file = "Non_scraped.txt"
    non_scraped_file_path = path2data + non_scraped_file
    
    L_tracks = []
    df_tracks = pd.read_csv("C:\\Users\\pawel\\Downloads\\flights\\xc_tracks.csv", index_col = 0)
    L_tracks = df_tracks["track"].tolist()
    
    ### open 10 drivers drivers                    
    driver0 = webdriver.Chrome(path2drivers + "ChromeDriver0\\chromedriver.exe")

    for i in range(20000, 25000):
        if L_tracks[i].find("dhv") > 0:
            driver0.get(L_tracks[i])
            time.sleep(randint(5, 10))
            window = win32gui.FindWindow(None, "www.dhv-xc.de - LEONARDO - Google Chrome")
            #win32gui.SetForegroundWindow(window)
            for i in range(10):
                try:
                    driver0.find_element_by_xpath('//*[@id="IgcDownloadPos"]').click() 
                    time.sleep(randint(3, 5))
                    # try clicking on one of the figures
                    mouse_click(560, 640) # first element
                    time.sleep(randint(3, 5))
                    mouse_click(620, 640) # first element
                except:
                    pass
    driver0.close()
    
#for i in range(len(L_tracks)):
#    if L_tracks[i].find("120342") > 0:
#        print(i)
