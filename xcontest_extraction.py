# -*- coding: utf-8 -*-
"""
Created on Thu Oct  4 18:35:53 2018

@author: BedynskiPa01
"""
## packages for webscraping igc files from the xcontest page
import time
import requests
from selenium import webdriver

## packages to move files from one folder to another
import glob
import shutil

## Create a folder in Downloads where all tracks will be stored
path2data = 'C:\\Users\\bedynskipa01\\Downloads\\Flights\\'
summary_file = "Roldanillo.txt"
summary_file_path = path2data + summary_file

## This handles the first page of 50 flights
url = "https://www.xcontest.org/world/en/flights-search/?list[sort]=pts&filter[point]=-76.2%204.45&"
url = url + "filter[radius]=10000&filter[mode]=START&filter[date_mode]=dmy&filter[date]=&"
url = url + "filter[value_mode]=dst&filter[min_value_dst]=&filter[catg]=&filter[route_types]="
url = url + "&filter[avg]=&filter[pilot]="
try:
    r = requests.get(url, stream = True)
    with open(summary_file_path, 'a', encoding='utf-8') as the_file:
        the_file.write(r.text)
except:
    print("Last file in history")

## Scrolls through pages of flights in xcontest 50 at a time and scrapes their content
## to get links to individual flights.
for i in range(1, 180):
    url = "https://www.xcontest.org/world/en/flights-search/?list[sort]=pts&list[start]=" 
    url = url + str(i * 50)
    url = url + "&filter[point]=-76.2%204.45&filter[radius]=10000&filter[mode]="
    url = url + "START&filter[date_mode]=dmy&filter[date]=&filter[value_mode]="
    url = url + "dst&filter[min_value_dst]=&filter[catg]=&filter[route_types]=&filter[avg]=&filter[pilot]="
    try:
        r = requests.get(url, stream = True)
        with open(summary_file_path, 'a', encoding='utf-8') as the_file:
            the_file.write(r.text)
    except:
        print("Last file in history")

## create a list of links to flights scraped to the file
L_tracks = []
with open(summary_file_path, 'r', encoding='utf-8') as f:
    for line in f:
        for word in line.split():
            if word.find('href="/world/en/flights/detail') == 0:
                track = "https:\\www.xcontest.org/"
                track = track + word[7:len(word) - 1]
                track = track.replace("/", "\\")
                L_tracks.append(track)


driver0 = webdriver.Chrome("C:\\Users\\bedynskipa01\\Desktop\\Python\\ChromeDrivers\\ChromeDriver0\\chromedriver.exe")
driver1 = webdriver.Chrome("C:\\Users\\bedynskipa01\\Desktop\\Python\\ChromeDrivers\\ChromeDriver1\\chromedriver.exe")
driver2 = webdriver.Chrome("C:\\Users\\bedynskipa01\\Desktop\\Python\\ChromeDrivers\\ChromeDriver2\\chromedriver.exe")
driver3 = webdriver.Chrome("C:\\Users\\bedynskipa01\\Desktop\\Python\\ChromeDrivers\\ChromeDriver3\\chromedriver.exe")
driver4 = webdriver.Chrome("C:\\Users\\bedynskipa01\\Desktop\\Python\\ChromeDrivers\\ChromeDriver4\\chromedriver.exe")
driver5 = webdriver.Chrome("C:\\Users\\bedynskipa01\\Desktop\\Python\\ChromeDrivers\\ChromeDriver5\\chromedriver.exe")
driver6 = webdriver.Chrome("C:\\Users\\bedynskipa01\\Desktop\\Python\\ChromeDrivers\\ChromeDriver6\\chromedriver.exe")
driver7 = webdriver.Chrome("C:\\Users\\bedynskipa01\\Desktop\\Python\\ChromeDrivers\\ChromeDriver7\\chromedriver.exe")
driver8 = webdriver.Chrome("C:\\Users\\bedynskipa01\\Desktop\\Python\\ChromeDrivers\\ChromeDriver8\\chromedriver.exe")
driver9 = webdriver.Chrome("C:\\Users\\bedynskipa01\\Desktop\\Python\\ChromeDrivers\\ChromeDriver9\\chromedriver.exe")

def myScrape(driver, track):
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
    driver.find_element_by_xpath('//*[@id="flight"]/div[1]/div[1]/table/tbody/tr[7]/th[1]/a').click()        

    ## compare the current url with the requested link
    first_part = track[0:6]
    second_part = track[7:len(track) + 1]
    track_to_compare = first_part + "//" + second_part.replace("\\", "/")
    if len(driver.current_url) == len(track_to_compare) + 5:
        pass
    else:
        time.sleep(30)
        driver.back()
        time.sleep(60)
        try:
            driver.find_element_by_xpath('//*[@id="flight"]/div[1]/div[1]/table/tbody/tr[7]/th[1]/a').click()
            if len(driver.current_url) == len(track_to_compare) + 5:
                pass
            else:
                print(driver.current_url)
        except:
            print(driver.current_url)

def scrape(start = 3008, finish = 3500): 
    for i in range(start, finish):
        if i % 10 == 0:    
            myScrape(driver0, L_tracks[i])
        elif i % 10 == 1:
            myScrape(driver1, L_tracks[i])
        elif i % 10 == 2:
            myScrape(driver2, L_tracks[i])
        elif i % 10 == 3:
            myScrape(driver3, L_tracks[i])
        elif i % 10 == 4:
            myScrape(driver4, L_tracks[i])
        elif i % 10 == 5:
            myScrape(driver5, L_tracks[i])
        elif i % 10 == 6:
            myScrape(driver6, L_tracks[i])
        elif i % 10 == 7:
            myScrape(driver7, L_tracks[i])
        elif i % 10 == 8:
            myScrape(driver8, L_tracks[i])
        elif i % 10 == 9:
            myScrape(driver9, L_tracks[i])

source_files = 'C:\\Users\\bedynskipa01\\Downloads\\*.igc'
target_folder = path2data

def move_files(source_files, target_folder):
## move files to the destination folder
    # retrieve file list
    filelist=glob.glob(source_files)
    for single_file in filelist:
        # move file with full paths as shutil.move() parameters
        try:
            shutil.move(single_file, target_folder)
        except:
            i = 0
            file_copied = False
            while file_copied == False:
                single_file_adj = single_file[0:len(single_file) - 4] + "_" + str(i) + ".igc"
                shutil.move(single_file, single_file_adj)
                try:
                    shutil.move(single_file_adj, target_folder)
                    file_copied = True
                except:
                    pass
                i = i + 1
            single_file = single_file_adj         