# GeoMap.py Map Plotting of World Travel.
# Creates folium map with layers indicating travel, plus photo pins.

#%%###################################################
# Import packages
######################################################
print('Importing python packages...')
import os
import datetime
import geopandas as gpd
import pandas as pd
import numpy as np
import folium       # for map
from folium import IFrame
from GPSPhoto import gpsphoto   # also requires exifread and piexif
import base64
from PIL import Image
print('Import complete.')

#%%###################################################
# Import geojson data
######################################################
print('Importing geo data...')
total_geo = gpd.read_file('geojson-data/total_geo.geojson')
print('Geo data import complete.')

#%%####################################################
# Create travel dataframes
#######################################################
print('Pulling in travel logs...')
#travelog_usa = pd.read_excel('usa_travel.xlsx')
travelog_usa = pd.read_csv('usa_travel.csv', sep=',')
#travelog_world = pd.read_excel('world_travel.xlsx')
travelog_world = pd.read_csv('world_travel.csv', sep=',')
travelog_total = travelog_world.append(travelog_usa)

total_geo = total_geo.merge(travelog_total, how = 'left').fillna(False)

person = travelog_world.columns[3:].tolist()    # read person names from columns
print('Found travel logs for {} and {}.'.format(person[0], person[1]))

both = total_geo.loc[np.logical_and(total_geo[person[0]], total_geo[person[1]])]
snake = total_geo.loc[np.logical_and(total_geo[person[0]], np.logical_not(total_geo[person[1]]))]
mongoose = total_geo.loc[np.logical_and(np.logical_not(total_geo[person[0]]), total_geo[person[1]])]
neither = total_geo.loc[np.logical_and(np.logical_not(total_geo[person[0]]), np.logical_not(total_geo[person[1]]))]

print('Travel logs complete.')

#%%###############################################
## Folium Plotting
##################################################
print('Creating Folium map baselayers...')
folium_loc = [51.519316, -0.1270625]    # start location. This can be customized to wherever the start should be.
zoom = 3
#   tiles='OpenStreetMap',   # looks nicest, but country names not in English
#   other tile options are 'OpenStreetMap', 'cartodbpositron', 'stamenwatercolor', 'stamentoner', 'stamenterrain', 'Mapbox Control Room', 'Mapbox Bright', 'MapQuest Open Aerial',
m = folium.Map(location = folium_loc,
    tiles='cartodbpositron',   # stamenwatercolor looks nice, but no names. Openstreetmap is good, but country names not in English
    zoom_start = zoom,
    min_zoom = 2,
    detect_retina = True,   # for retina displays
    max_bounds = True,
    min_lat = -90, max_lat = 90, min_lon = -180, max_lon = 180,
    no_wrap = True,
    control_scale = True
    )
#    tiles = 'http://tile.stamen.com/terrain-labels/'+str(zoom)+'/'+str(folium_loc[0])+'/'+str(folium_loc[1])+'.png',
#    attr='Map tiles by <a href="http://stamen.com">Stamen Design</a>, <a href="http://creativecommons.org/licenses/by/3.0">CC BY 3.0</a> &mdash; Map data &copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors'

folium.GeoJson(both.geometry,
    name = 'Both Explored',
    style_function=lambda feature: {
        'fillColor': '#c48efd',     # xkcd:liliac
        'fillOpacity':0.75,
        'color': 'black',
        'weight': 2,
        #'dashArray': '5, 5'
    }).add_to(m)
folium.GeoJson(snake.geometry,
    name= person[0] + ' Only',
    style_function=lambda feature: {
        'fillColor': '#0cb577',     # xckd:green teal
        'color': 'black',
        'fillOpacity':0.75,
        'weight': 2,
        #'dashArray': '5, 5'
    }).add_to(m)
folium.GeoJson(mongoose.geometry,
    name = person[1] + ' Only',
    style_function=lambda feature: {
        'fillColor': '#ff6163',    # xkcd: coral pink
        'fillOpacity':0.75,
        'color': 'black',
        'weight': 2,
        #'dashArray': '5, 5'
    }).add_to(m)
folium.GeoJson(neither.geometry,
    name = 'Not Explored Yet',
    style_function=lambda feature: {
        'fillColor': '#fefcaf',     # xkcd: parchment
        'fillOpacity':0.0,
        'color': 'black',
        'weight': 2,
        #'dashArray': '5, 5'
    }).add_to(m)

folium.LayerControl().add_to(m)
#folium.LayerControl(collapsed=False).add_to(m)

now = datetime.datetime.today()
filepath = 'travelmap{}.html'.format(now.strftime('%Y%m%d'))
m.save(filepath)
print('Done creating basemap.')

##############################
#Now for the picture popups...
##############################
print('Importing photos.')

file_list = []
thumbnails = []
for photo in os.listdir(os.curdir+'/pics/'):
    if photo.endswith('.jpg'):
        try:
            file_list.append(photo)
        except:
            print('Skipping {}: Thumbnail does not exist.'.format(photo))

def create_popup(jpg):
    '''Creates popups from filename input'''
    data = gpsphoto.getGPSData('pics/{}'.format(jpg))
    width, height = Image.open('pics/thumbnail/{}'.format(jpg)).size
    encoded = base64.b64encode(open('pics/thumbnail/{}'.format(jpg), 'rb').read()).decode()
    html = '<img src="data:image/jpeg;base64, {}" align="center" style="max-width:100%; height:auto; min-width: 330px;">'.format
    #width:80vw in line above would scale to the view size, which maybe we don't need here.
    iframe = IFrame(html(encoded), width=width+20, height=height+20)
    popup = folium.Popup(iframe, max_width=1200)   # max_width = 75%
    icon = folium.Icon(color='cadetblue', icon='camera')    # can add popup_anchor = (20,20)   this is relative to the pin though
    marker = folium.Marker(location=[data['Latitude'], data['Longitude']], popup=popup, icon=icon)
    return marker, data

print('Creating {} photo pins.'.format(len(file_list)))

name = []
Latitude = []
Longitude = []
Altitude = []
Date = []
UTC_Time = []

for jpg in file_list:
    marker, data = create_popup(jpg)
    marker.add_to(m)
    # fill in data for photolog
    name.append(jpg)
    Latitude.append(data['Latitude'])
    Longitude.append(data['Longitude'])
    try:
        Altitude.append(data['Altitude'])
    except:
        Altitude.append(0)
    try:
        Date.append(data['Date'])
    except:
        Date.append(now.strftime('%Y/%m/%d'))  # if we don't know, just fill in the current time
    try:
        UTC_Time.append(data['UTC-Time'])
    except:
        UTC_Time.append(now.strftime('%H:%M:%S'))  # if we don't know, just fill in the current time

photolog = pd.DataFrame({'Name':name, 'Latitude':Latitude, 'Longitude':Longitude, 'Altitude':Altitude, 'Date':Date, 'UTC_Time':UTC_Time})
#print(photolog)    # only for troubleshooting & development
photolog.to_csv('Photolog.txt', index = False, sep = '\t')

print('Saving final map to .html...')
m.save(filepath)
print('Map creation complete.')
