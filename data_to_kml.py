# -*- coding: utf-8 -*-
"""
Created on Sat Oct 20 09:23:06 2018
@author: Pawel Bedynski
"""
import pandas as pd
import numpy as np
import simplekml
from simplekml import Kml
###############################################################################
from datetime import datetime
import multiprocessing

### KML for the the morning        
def prep_lift(num):  
    divisor = 100
    if num == 0:
        data_to_show = data_to_show_large[10000000:50000000].reset_index()
        file_name = "therm_h1"      
    elif num == 1:
        data_to_show = data_to_show_large[50000000:90000000].reset_index()
        file_name = "therm_h2"
    elif num == 2:
        data_to_show = data_to_show_large[110000000:150000000].reset_index()
        file_name = "therm_v1"
    elif num == 3:    
        data_to_show = data_to_show_large[150000000:190000000].reset_index()
        file_name = "therm_v2"    
    lon_col = "lon" 
    lat_col = "lat"  
    data_col = "data"
    ### initialise the file
    lines = []
    lines.append('<?xml version="1.0" encoding="UTF-8"?>\n')
    lines.append('<kml xmlns="http://www.opengis.net/kml/2.2" xmlns:gx="http://www.google.com/kml/ext/2.2">\n')
    lines.append('    <Document id="{}">\n'.format(5))
    lines.append('        <open>1</open>\n')
    lines.append('    </Document>\n')
    lines.append('</kml>')
    ### create lines that represent thermals
    for i in range(1, len(data_to_show) - 1):
        ### style and line ids and start the file
        style_number = i * 4
        x1 = data_to_show[lon_col][i]
        y1 = data_to_show[lat_col][i]
        z1 = data_to_show[data_col][i] / divisor
        x2 = data_to_show[lon_col][i + 1]
        y2 = data_to_show[lat_col][i + 1]
        z2 = data_to_show[data_col][i + 1] / divisor            
        if z1 > 3 or z2 > 3:
            width = 3
            if z1 < 5 or z2 < 5:
                color = 'ff14f0ff'
            elif z1 < 10 or z2 < 10:
                width = 5
                color = 'ff1478ff'
            else:
                width = 7
                color = 'ff1400ff'
            lines_start = lines.index('        <open>1</open>\n')
            lines.insert(lines_start, '        <Style id="{}">\n'.format(style_number + 4))
            lines.insert(lines_start + 1, '            <LineStyle id="{}">\n'.format(style_number + 5))
            lines.insert(lines_start + 2, '                <color>{}</color>\n'.format(color))
            lines.insert(lines_start + 3, '                <colorMode>normal</colorMode>\n')
            lines.insert(lines_start + 4, '                <width>{}</width>\n'.format(width))
            lines.insert(lines_start + 5, '            </LineStyle>\n')
            lines.insert(lines_start + 6, '        </Style>\n')        
            lines.insert(len(lines) - 2, '        <Placemark id="{}">\n'.format(style_number + 3))
            lines.insert(len(lines) - 2, '            <name>line {}</name>\n'.format(i + 1))
            lines.insert(len(lines) - 2, '            <styleUrl>#{}</styleUrl>\n'.format(style_number + 4))
            lines.insert(len(lines) - 2, '            <LineString id="{}">\n'.format(style_number + 2))
            line_segment = '                <coordinates>'
            line_segment = line_segment + str(x1) + ',' + str(y1) + ',' + str(z1) + ' ' + str(x2) + ',' + str(y2) + ',' + str(z2)
            line_segment = line_segment + '</coordinates>\n'
            lines.insert(len(lines) - 2, line_segment)
            lines.insert(len(lines) - 2, '                <altitudeMode>relativetoground</altitudeMode>\n')
            lines.insert(len(lines) - 2, '            </LineString>\n')   
            lines.insert(len(lines) - 2, '        </Placemark>\n')   
    f = open(path2grid + file_name + ".kml", "w")
    for line in lines:
        f.write(line)
    f.close()
    return len(lines)

# need to figure out what this does
def new_prep_lift_kml_per_hour(hours, data_to_show):
    for hour in hours:    
        lon_col = "lon" + str(hour) 
        lat_col = "lat" + str(hour)   
        data_col = "data" + str(hour)
       
        ### calculate max lift
        max_lift = data_to_show[data_col].max()
        print(lon_col, lat_col, data_col, max_lift)
    
        ### initialise the file
        lines = []
        lines.append('<?xml version="1.0" encoding="UTF-8"?>\n')
        lines.append('<kml xmlns="http://www.opengis.net/kml/2.2" xmlns:gx="http://www.google.com/kml/ext/2.2">\n')
        lines.append('    <Document id="{}">\n'.format(5))
        lines.append('        <open>1</open>\n')
        lines.append('    </Document>\n')
        lines.append('</kml>')
    
        ### create lines that represent thermals
        for i in range(1, len(data_to_show) - 1):
            ### style and line ids and start the file
            style_number = i * 4
            x1 = -data_to_show[lon_col][i]
            y1 = data_to_show[lat_col][i]
            z1 = data_to_show[data_col][i] / 100
            x2 = -data_to_show[lon_col][i + 1]
            y2 = data_to_show[lat_col][i + 1]
            z2 = data_to_show[data_col][i + 1] / 100            
            if z1 > 3 or z2 > 3:
                width = 3
                if z1 < 8 or z2 < 8:
                    color = 'ff14f0ff'
                elif z1 < 20 or z2 < 20:
                    width = 5
                    color = 'ff1478ff'
                else:
                    width = 7
                    color = 'ff1400ff'
    
                lines_start = lines.index('        <open>1</open>\n')
                lines.insert(lines_start, '        <Style id="{}">\n'.format(style_number + 4))
                lines.insert(lines_start + 1, '            <LineStyle id="{}">\n'.format(style_number + 5))
                lines.insert(lines_start + 2, '                <color>{}</color>\n'.format(color))
                lines.insert(lines_start + 3, '                <colorMode>normal</colorMode>\n')
                lines.insert(lines_start + 4, '                <width>{}</width>\n'.format(width))
                lines.insert(lines_start + 5, '            </LineStyle>\n')
                lines.insert(lines_start + 6, '        </Style>\n')        
                lines.insert(len(lines) - 2, '        <Placemark id="{}">\n'.format(style_number + 3))
                lines.insert(len(lines) - 2, '            <name>line {}</name>\n'.format(i + 1))
                lines.insert(len(lines) - 2, '            <styleUrl>#{}</styleUrl>\n'.format(style_number + 4))
                lines.insert(len(lines) - 2, '            <LineString id="{}">\n'.format(style_number + 2))
                line_segment = '                <coordinates>'
                line_segment = line_segment + str(x1) + ',' + str(y1) + ',' + str(z1) + ' ' + str(x2) + ',' + str(y2) + ',' + str(z2)
                line_segment = line_segment + '</coordinates>\n'
                lines.insert(len(lines) - 2, line_segment)
                lines.insert(len(lines) - 2, '                <altitudeMode>relativetoground</altitudeMode>\n')
                lines.insert(len(lines) - 2, '            </LineString>\n')   
                lines.insert(len(lines) - 2, '        </Placemark>\n')
            
        f = open(path2grid + "hours\\Roldanillo_" + str(hour) + "_thermals.kml", "w")
        for line in lines:
            f.write(line)
        f.close()

        
### KML for the the morning        
def prep_morning_lift(data_to_show, day_part, divisor):  
    lon_col = "lon" 
    lat_col = "lat"  
    data_col = "data"
    
    ### initialise the file
    lines = []
    lines.append('<?xml version="1.0" encoding="UTF-8"?>\n')
    lines.append('<kml xmlns="http://www.opengis.net/kml/2.2" xmlns:gx="http://www.google.com/kml/ext/2.2">\n')
    lines.append('    <Document id="{}">\n'.format(5))
    lines.append('        <open>1</open>\n')
    lines.append('    </Document>\n')
    lines.append('</kml>')
    
    ### create lines that represent thermals
    for i in range(1, len(data_to_show) - 1):
        ### style and line ids and start the file
        style_number = i * 4
        x1 = -data_to_show[lon_col][i]
        y1 = data_to_show[lat_col][i]
        z1 = data_to_show[data_col][i] / divisor
        x2 = -data_to_show[lon_col][i + 1]
        y2 = data_to_show[lat_col][i + 1]
        z2 = data_to_show[data_col][i + 1] / divisor            
        if z1 > 5 or z2 > 5:
            width = 3
            if z1 < 10 or z2 < 10:
                color = 'ff14f0ff'
            elif z1 < 20 or z2 < 20:
                width = 5
                color = 'ff1478ff'
            else:
                width = 7
                color = 'ff1400ff'
    
            lines_start = lines.index('        <open>1</open>\n')
            lines.insert(lines_start, '        <Style id="{}">\n'.format(style_number + 4))
            lines.insert(lines_start + 1, '            <LineStyle id="{}">\n'.format(style_number + 5))
            lines.insert(lines_start + 2, '                <color>{}</color>\n'.format(color))
            lines.insert(lines_start + 3, '                <colorMode>normal</colorMode>\n')
            lines.insert(lines_start + 4, '                <width>{}</width>\n'.format(width))
            lines.insert(lines_start + 5, '            </LineStyle>\n')
            lines.insert(lines_start + 6, '        </Style>\n')        
            lines.insert(len(lines) - 2, '        <Placemark id="{}">\n'.format(style_number + 3))
            lines.insert(len(lines) - 2, '            <name>line {}</name>\n'.format(i + 1))
            lines.insert(len(lines) - 2, '            <styleUrl>#{}</styleUrl>\n'.format(style_number + 4))
            lines.insert(len(lines) - 2, '            <LineString id="{}">\n'.format(style_number + 2))
            line_segment = '                <coordinates>'
            line_segment = line_segment + str(x1) + ',' + str(y1) + ',' + str(z1) + ' ' + str(x2) + ',' + str(y2) + ',' + str(z2)
            line_segment = line_segment + '</coordinates>\n'
            lines.insert(len(lines) - 2, line_segment)
            lines.insert(len(lines) - 2, '                <altitudeMode>relativetoground</altitudeMode>\n')
            lines.insert(len(lines) - 2, '            </LineString>\n')   
            lines.insert(len(lines) - 2, '        </Placemark>\n')
        
    if day_part == "morning":
        f = open(path2grid + "hours\\Morn_therm.kml", "w")
    else:
        f = open(path2grid + "hours\\Aftn_therm.kml", "w")
    for line in lines:
        f.write(line)
    f.close()
    
    
### KML for the afternoon
def prep_afternoon_lift(data_to_show, day_part, divisor):  
    lon_col = "lon" 
    lat_col = "lat"  
    data_col = "data"
       
    ### calculate max lift
    max_lift = data_to_show[data_col].max()
    print(lon_col, lat_col, data_col, max_lift)
    
    ### initialise the file
    lines = []
    lines.append('<?xml version="1.0" encoding="UTF-8"?>\n')
    lines.append('<kml xmlns="http://www.opengis.net/kml/2.2" xmlns:gx="http://www.google.com/kml/ext/2.2">\n')
    lines.append('    <Document id="{}">\n'.format(5))
    lines.append('        <open>1</open>\n')
    lines.append('    </Document>\n')
    lines.append('</kml>')
    
    ### create lines that represent thermals
    for i in range(1, len(data_to_show) - 1):
        ### style and line ids and start the file
        style_number = i * 4
        x1 = -data_to_show[lon_col][i]
        y1 = data_to_show[lat_col][i]
        z1 = data_to_show[data_col][i] / divisor
        x2 = -data_to_show[lon_col][i + 1]
        y2 = data_to_show[lat_col][i + 1]
        z2 = data_to_show[data_col][i + 1] / divisor            
        if z1 > 25 or z2 > 25:
            width = 3
            if z1 < 40 or z2 < 50:
                color = 'ff14f0ff'
            elif z1 < 70 or z2 < 70:
                width = 5
                color = 'ff1478ff'
            else:
                width = 7
                color = 'ff1400ff'
    
            lines_start = lines.index('        <open>1</open>\n')
            lines.insert(lines_start, '        <Style id="{}">\n'.format(style_number + 4))
            lines.insert(lines_start + 1, '            <LineStyle id="{}">\n'.format(style_number + 5))
            lines.insert(lines_start + 2, '                <color>{}</color>\n'.format(color))
            lines.insert(lines_start + 3, '                <colorMode>normal</colorMode>\n')
            lines.insert(lines_start + 4, '                <width>{}</width>\n'.format(width))
            lines.insert(lines_start + 5, '            </LineStyle>\n')
            lines.insert(lines_start + 6, '        </Style>\n')        
            lines.insert(len(lines) - 2, '        <Placemark id="{}">\n'.format(style_number + 3))
            lines.insert(len(lines) - 2, '            <name>line {}</name>\n'.format(i + 1))
            lines.insert(len(lines) - 2, '            <styleUrl>#{}</styleUrl>\n'.format(style_number + 4))
            lines.insert(len(lines) - 2, '            <LineString id="{}">\n'.format(style_number + 2))
            line_segment = '                <coordinates>'
            line_segment = line_segment + str(x1) + ',' + str(y1) + ',' + str(z1) + ' ' + str(x2) + ',' + str(y2) + ',' + str(z2)
            line_segment = line_segment + '</coordinates>\n'
            lines.insert(len(lines) - 2, line_segment)
            lines.insert(len(lines) - 2, '                <altitudeMode>relativetoground</altitudeMode>\n')
            lines.insert(len(lines) - 2, '            </LineString>\n')   
            lines.insert(len(lines) - 2, '        </Placemark>\n')
        
    if day_part == "morning":
        f = open(path2grid + "hours\\Morn_therm.kml", "w")
    else:
        f = open(path2grid + "hours\\Aftn_therm.kml", "w")
    for line in lines:
        f.write(line)
    f.close()

# need to figure out what this does
def prep_lift_kml_per_hour(hours, data_to_show):
    for hour in hours:
        ### create the kml file
        kml = Kml(open=1)
        ### name columns according to hour of day
        lon_col = "lon" + str(hour) 
        lat_col = "lat" + str(hour)   
        data_col = "data" + str(hour)
        
        ### calculate max lift
        max_lift = data_to_show[data_col].max()

        ### create lines that represent thermals
        for i in range(len(data_to_show) - 1):
            x1 = -data_to_show[lon_col][i]
            y1 = data_to_show[lat_col][i]
            z1 = data_to_show[data_col][i] / max_lift * 100
            x2 = -data_to_show[lon_col][i + 1]
            y2 = data_to_show[lat_col][i + 1]
            z2 = data_to_show[data_col][i + 1] / max_lift * 100
            
            if z1 > 1 or z2 > 1:
                line_name = "line " + str(i)
                linestring = kml.newlinestring(name = line_name)
                linestring.coords = [(x1, y1, z1), (x2, y2, z2)]
                linestring.altitudemode = simplekml.AltitudeMode.relativetoground
                linestring.style.linestyle.width = 3
                if z1 < 20 or z2 < 20:
                    linestring.style.linestyle.color = simplekml.Color.yellow
                elif z1 < 40 or z2 < 40:
                    linestring.style.linestyle.color = simplekml.Color.orange
                    linestring.style.linestyle.width = 5
                else:
                    linestring.style.linestyle.color = simplekml.Color.red
                    linestring.style.linestyle.width = 7
                ### linestring.extrude = 1
        
        kml_file_name = "Roldanillo_" + str(hour) + "_thermals.kml"
        kml.save(path2grid + "hours\\" + kml_file_name)


# this just computes the sink grid perhaps - need to figure out if I need it
def prep_sink_kml_per_hour(hours, data_to_show):
    for hour in hours:
        ### create the kml file
        kml = Kml(open=1)
        ### name columns according to hour of day
        lon_col = "lon" + str(hour) 
        lat_col = "lat" + str(hour)   
        data_col = "data" + str(hour)
        ### create lines that represent thermals
        for i in range(len(data_to_show) - 1):
            x1 = -data_to_show[lon_col][i]
            y1 = data_to_show[lat_col][i]
            z1 = data_to_show[data_col][i]
            x2 = -data_to_show[lon_col][i + 1]
            y2 = data_to_show[lat_col][i + 1]
            z2 = data_to_show[data_col][i + 1]
            if z1 < -100 or z2 < -100:
                line_name = "line " + str(i)
                linestring = kml.newlinestring(name = line_name)
                linestring.coords = [(x1, y1), (x2, y2)]
                linestring.altitudemode = simplekml.AltitudeMode.absolute
                linestring.style.linestyle.width = 3
                if z1 > -200 or z2 > -200:
                    linestring.style.linestyle.color = simplekml.Color.green
                elif z1 > -400 or z2 > -400:
                    linestring.style.linestyle.color = simplekml.Color.blue
                    linestring.style.linestyle.width = 6
                else:
                    linestring.style.linestyle.color = simplekml.Color.black
                    linestring.style.linestyle.width = 9
                ### linestring.extrude = 1
        
        kml_file_name = "Roldanillo_" + str(hour) + "_sinks.kml"
        kml.save(path2grid + "hours\\" + kml_file_name)

# calculate wind grid
def prep_wind_kml_per_hour(data_to_show):
    ### create the kml file
    kml = Kml(open=1)
    ### name columns according to hour of day
    lon_col = "lon" 
    lat_col = "lat"  
    data_col = "data"
    ### create lines that represent thermals
    ### calculate centre of the small grid
    ### place the line segment in the centre
    ### take wind speed and direction and calculate coordinates
    ### of the end point of the line segment
    ### add the arrow pointer
    for i in range(1, len(data_to_show) - 1):
        x1 = -data_to_show[lon_col][i]
        y1 = data_to_show[lat_col][i]
        z1 = data_to_show[data_col][i]
        x2 = -data_to_show[lon_col][i + 1]
        y2 = data_to_show[lat_col][i + 1]
        z2 = data_to_show[data_col][i + 1]
        if z1 > 0 or z2 > 0:
            line_name = "line " + str(i)
            linestring = kml.newlinestring(name = line_name)
            linestring.coords = [(x1, y1), (x2, y2)]
            linestring.altitudemode = simplekml.AltitudeMode.relativetoground
            linestring.style.linestyle.width = 10
            linestring.iconstyle.icon.href = 'http://earth.google.com/images/kml-icons/track-directional/track-0.png'
            linestring.style.linestyle.color = '99ffac59'
    
    kml_file_name = "Roldanillo_wind.kml"
    kml.save(path2grid + "hours\\" + kml_file_name)
    

### setting up paths to various data files
start_time = datetime.now()
path2grid = 'D:\\Flights\\Grid\\'
path2grid = '/mnt/d/flights/grid/'
# change location file name to run kmls for another location
location_file_name = "Perugia"
data_to_show_file = path2grid + location_file_name + ".csv"

data_to_show_large = pd.read_csv(data_to_show_file, sep = ",")
data_to_show_large = data_to_show_large.drop(['Unnamed: 0'], axis = 1)

# Better protect your main function when you use multiprocessing
pool = multiprocessing.Pool(processes = 4)
results = pool.map(prep_lift, range(4))
pool.close()
pool.join()
for result in results:
# prints the result string in the main process
    print(result)
print(datetime.now() - start_time)
