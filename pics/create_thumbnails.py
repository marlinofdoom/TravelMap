import glob
from PIL import Image
from GPSPhoto import gpsphoto
import datetime

# get all the jpg files from the current folder
for infile in glob.glob("*.jpg"):
  im = Image.open(infile)
  width, height = im.size
  if width > height:
      new_width = 400
      new_height = (new_width/width) * height
  else:
      new_height = 400
      new_width = (new_height/height) * width
  info = gpsphoto.getGPSData(infile)
  #im.modGPSData(info)
  # convert to thumbnail image
  im.thumbnail((new_width, new_height), Image.ANTIALIAS)
  im.save('thumbnail/' + infile, 'JPEG')
  new_image = gpsphoto.GPSPhoto()
  new_image = gpsphoto.GPSPhoto('thumbnail/' + infile)
  try:
      alt_data = int(info['Altitude'])
  except:
      alt_data = 0
  try:
      time_data = info['Date'][-4:] + ':' + info['Date'][:2] + ':' + info['Date'][3:5] + ' ' + info['UTC-Time']
  except:
      time_data = datetime.datetime.now()
  data = gpsphoto.GPSInfo(
        (info['Latitude'], info['Longitude']),
        alt = alt_data,
        timeStamp = time_data
        )
  new_image.modGPSData(data, 'thumbnail/' + infile)
