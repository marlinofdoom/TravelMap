# batch_add_GPS.py
# script to add GPS coordinates and/or timestamps to photos.
# Requires input from Photolog.txt, and images with names corresponding to log entries to be in the same folder.

import pandas as pd
from GPSPhoto import gpsphoto   # also requires exifread and piexif
import datetime

error_count = 0
input = pd.read_csv('Photolog.txt', sep = '\t', skip_blank_lines = True).dropna()
for row in input.itertuples(index=False):
    try:
        jpg = row.Name
        time = datetime.datetime.strptime(' '.join([row.Date, row.UTC_Time]), '%m/%d/%Y %H:%M:%S')
        info = gpsphoto.GPSInfo(
            (row.Latitude, row.Longitude),
            alt = int(row.Altitude),
            timeStamp = time.strftime('%Y:%m:%d %H:%M:%S'))
        photo = gpsphoto.GPSPhoto(jpg)
        photo.modGPSData(info, 'gps_'+jpg)
        print('Writing file: gps_{}'.format(jpg))
    except:
        error_count += 1    # rudimentary, generic error checking/notification

print('Batch complete with {} errors.'.format(error_count))
