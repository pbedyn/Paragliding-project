# -*- coding: utf-8 -*-
"""
Created on Thu Oct  4 18:35:53 2018
@author: Pawel Bedynski
"""

# DONE: clean up after execution - shut down the 10 chromedriver windows
# DONE: verify if a file already exists, if yes, skip
#       actually it overwrites the file
# TODO: create the folder structure
# TODO: determine based on location of take off which region to allocate the flight to
#       regions to be split based on lat, lon e.g. roughly North-West Europe, North-East Europe etc.
#       
# TODO: move files to folders based on the month of flight

### import standard Python libraries for execution
import os
import time
import threading

### import webscraping libraries
import requests
from selenium import webdriver

### import pandas and numpy for handling datatables
import pandas as pd
import numpy as np

### set path to a folder in Downloads where all tracks will be stored
path2data = 'C:\\Users\\pbedyn\\Downloads\\'
path2file = 'C:\\Users\\pbedyn\\Downloads\\'

### create the file where list of flights will be stored
summary_file = "Poland.txt"
summary_file_path = path2data + summary_file

### function to create a new directory
def create_folder(directory):
    try:
        if not os.path.exists(directory):
            os.makedirs(directory)
    except OSError:
        print("Error creating directory. " + directory)

### take a break every 50 flights
def take_break(i):
    if i > 0 and i % 50 == 0:
        print("Taking a break every 50th flight")
        time.sleep(60)

###############################################################################
### Function doing the actual scraping - called by each google driver #########
### Error handling should be improved as it still fails sometimes
def my_scrape(driver, track):
    """ Opens a driver and scrapes the track """
    driver.get(track)
    driver.execute_script("window.scrollTo(0, 300)")
    time.sleep(5)
    driver.execute_script("window.scrollTo(0, 600)")
    time.sleep(5)
    driver.execute_script("window.scrollTo(0, 900)")
    time.sleep(5)
    driver.execute_script("window.scrollTo(0, 0)")
    time.sleep(5)
    try:
        driver.find_element_by_xpath('//*[@id="main-content"]/article/div/div[1]/div[2]/div/a').click()
    except:
        driver.find_element_by_xpath('//*[@id="main-content"]/article/div/div[1]/div[1]/div/a').click()
    
    # get current url
    url = driver.current_url
    file_name = path2folder + "\\" + os.path.basename(url)
    
    r = requests.get(url)
    with open(file_name, 'w', encoding='utf-8') as the_file:
        the_file.write(r.text)

### Invoke the right driver and scrape track i
def select_driver(i):
    my_scrape(eval("driver" + str(i % 10)), L_tracks[i])
    #outcomes[i % 10] = i % 10
    print(i)
    take_break(i)

### Function to close all drivers    
def close_drivers():
    for i in range(10):
        eval("driver" + str(i)).close()

### Modify this function in such way that on error it restarts scraping
### Function to open webdrivers
def scrape_launch_sites():
    ### create the file where list of flights will be stored
    launch_sites_file = "Launch_sites.txt"
    launch_sites_file_path = path2data + launch_sites_file

#    url = "http://xcportal.pl/launch-sites"
#    try:
#        r = requests.get(url)
#        with open(launch_sites_file_path, 'w', encoding='utf-8') as the_file:
#            the_file.write(r.text)
#    except:
#        print("Last file in history")
#    
#    for i in range(163):
#        url = "http://xcportal.pl/launch-sites?title=&page=" + str(i)
#        time.sleep(60)
#        try:
#            r = requests.get(url)
#            with open(launch_sites_file_path, 'a', encoding='utf-8') as the_file:
#                the_file.write(r.text)
#        except:
#            print("Last page in repository")
        
    L_sites = []
    with open(launch_sites_file_path, 'r', encoding='utf-8') as f:
        for line in f:
            for word in line.split():
                ### word.find gives the position of the fragment in the string
                if word.find('href="/node/') == 0:
                    site = "http://xcportal.pl/node/"
                    site = site + word[12:18]
                    site = site.replace("/", "\\")
                    # append only tracks ending with a digit
                    if site[len(site) - 1].isdigit():
                        L_sites.append(site)
                    elif site[len(site) - 1] == '"':
                        L_sites.append(site[0:len(site) - 1])
    L_sites = list(set(L_sites))
    return L_sites

### execution of the mian    
if __name__ == "__main__":
    
#    L_sites = scrape_launch_sites()
    
    ### go through the sites and get the number of flights
#    for i in range(2100, 2200):
#    url = L_sites[i] + "?order=field_flight_max_points&sort=desc"
#    url = url.replace("\\", "/")
    url = 'http://xcportal.pl/node/16838?order=field_flight_max_points&sort=desc'
    #launch_site_number = L_sites[i][24:len(L_sites[i])]
    launch_site_number = 16838
    path2file = path2data + "Launch_sites\\"
    site_file = path2file + str(launch_site_number) + ".txt"
    try:
        r = requests.get(url)
        with open(site_file, 'w', encoding='utf-8') as the_file:
            the_file.write(r.text)
    except:
        print("Last file in history")
    time.sleep(30)
    
    ### create a list of links to flights scraped to the file
    L_tracks = []
    with open(site_file, 'r', encoding='utf-8') as f:
        for line in f:
            for word in line.split():
                ### word.find gives the position of the fragment in the string
                if word.find('href="/node/') == 0:
                    track = "http://xcportal.pl/node/"
                    track = track + word[12:len(word) - 16]
                    track = track.replace("/", "\\")
                    # append only tracks ending with a digit
                    if track[len(track) - 1].isdigit():
                        L_tracks.append(track)
    
    if len(L_tracks) > 0:
        
        ### create folder to store flights
        path2folder = path2file + str(launch_site_number)
        create_folder(path2folder)
        
        
        add_to_list = 10 - len(L_tracks) % 10
        for i in range(add_to_list):
            L_tracks.append(L_tracks[len(L_tracks) - 1])
    
        ### open drivers                    
        driver0 = webdriver.Chrome("C:\\Users\\pbedyn\\Downloads\\Chromedrivers\\ChromeDriver0\\chromedriver.exe")
        driver1 = webdriver.Chrome("C:\\Users\\pbedyn\\Downloads\\Chromedrivers\\ChromeDriver1\\chromedriver.exe")
        driver2 = webdriver.Chrome("C:\\Users\\pbedyn\\Downloads\\Chromedrivers\\ChromeDriver2\\chromedriver.exe")
        driver3 = webdriver.Chrome("C:\\Users\\pbedyn\\Downloads\\Chromedrivers\\ChromeDriver3\\chromedriver.exe")
        driver4 = webdriver.Chrome("C:\\Users\\pbedyn\\Downloads\\Chromedrivers\\ChromeDriver4\\chromedriver.exe")
        driver5 = webdriver.Chrome("C:\\Users\\pbedyn\\Downloads\\Chromedrivers\\ChromeDriver5\\chromedriver.exe")
        driver6 = webdriver.Chrome("C:\\Users\\pbedyn\\Downloads\\Chromedrivers\\ChromeDriver6\\chromedriver.exe")
        driver7 = webdriver.Chrome("C:\\Users\\pbedyn\\Downloads\\Chromedrivers\\ChromeDriver7\\chromedriver.exe")
        driver8 = webdriver.Chrome("C:\\Users\\pbedyn\\Downloads\\Chromedrivers\\ChromeDriver8\\chromedriver.exe")
        driver9 = webdriver.Chrome("C:\\Users\\pbedyn\\Downloads\\Chromedrivers\\ChromeDriver9\\chromedriver.exe")
        
        threads = []
        add_to_loop = 0
        if len(L_tracks) % 10 > 0:
            add_to_loop = 1
        for j in range(len(L_tracks) // 10 + add_to_loop):
            for i in range(10):
                t = threading.Thread(target=select_driver, args=(j*10 + i,))
                threads.append(t)
                t.start()
            # Wait for all threads to complete
            for t in threads:
                t.join()
            
        close_drivers()
