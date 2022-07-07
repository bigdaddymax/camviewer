import os
from flask import Flask
from flask import stream_with_context, Response, redirect
import cv2
import numpy as np
import time

app = Flask(__name__)

rootDir = '/opt/python/smartcam/video'

@app.route('/')
def get_cams():
    global rootdir
    cams = ''
    for camName in os.listdir(rootDir):
        cams = cams + '<a href="/'+ camName +'">' + camName + '</a><br>'
    return cams

@app.route('/<camName>')
def get_cam_subdirs(camName):
   global rootDir
   urls = ''
   years = [];
   for date in os.listdir(rootDir + '/' + camName):
       years.append(date.split('-')[0])
   years_set = set(years)
   for year in years_set:
       urls = urls + '<a href="/' + camName + '/' + year + '">' + year + '</a><br>'
   return urls

@app.route('/<camName>/<year>')
def get_cam_subdirs_year(camName, year):
   global rootDir
   urls = ''
   months = []
   for date in os.listdir(rootDir + '/' + camName):
       date_split = date.split('-')
       if date_split[0] == year:
          months.append(date_split[1])
   months_set = set(months)

   for month in sorted(months_set):
       urls = urls + '<a href="/' + camName + '/' + year + '/' + month + '">' + year + '-' + month + '</a><br>'
   return urls

@app.route('/<camName>/<year>/<month>')
def get_cam_subdirs_month(camName, year, month):
   global rootDir
   urls = ''
   days = []
   for date in os.listdir(rootDir + '/' + camName):
       date_split = date.split('-')
       if date_split[0] == year and date_split[1] == month:
          days.append(date_split[2])
   days_set = set(days)
   for day in sorted(days_set):
       urls = urls + '<a href="/' + camName + '/' + year + '/' + month + '/' + day + '">' + year + '-' + month + '-' + day + '</a><br>'
   return urls

@app.route('/<camName>/<year>/<month>/<day>')
def get_cam_subdirs_day(camName, year, month, day):
   global rootDir
   urls = ''
   for clip in os.listdir(rootDir + '/' + camName + '/' + year + '-' + month + '-' + day):
       urls = urls + '<a href="/' + camName + '/' + year + '/' + month + '/' + day + '/' + clip + '">' + clip +  '</a><br>'
   return urls

#@app.route('/<camName>/<year>/<month>/<day>/<clip>')
#def get_cam_subdirs(camName):
#   global rootDir
#   urls = ''
#   for date in os.listdir(rootDir + '/' + camName):
#       urls = urls + '<a href="/' + camName + '/' + date + '">' + date + '</a><br>'
#   return urls

#@app.route('/<camName>/<date>')
#def get_cam_date_subdirs(camName, date):
#   global rootDir
#   urls = ''
#   for clip in os.listdir(rootDir + '/' + camName + '/' + date):
#       urls = urls + '<a href="/' + camName + '/' + date + '/' + clip + '">' + clip + '</a><br>'
#   return urls


@app.route('/<camName>/<year>/<month>/<day>/<clip>')
def show_clip(camName, year, month, day, clip):
   def readStream(clip):
      fps = clip.get(cv2.CAP_PROP_FPS);
      while clip.isOpened():
          time.sleep(1/(fps))
          ret, frame = clip.read()
          if frame is None:
             return
          (flag, jpg) = cv2.imencode('.jpg', frame)
          if not flag:
              print('Error')
              continue
          yield (b'--frame\r\nContent-Type: image/jpeg\r\n\r\n' + bytearray(jpg) + b'\r\n')

   global rootDir
   f = cv2.VideoCapture(rootDir + '/' + camName + '/' + year + '-' + month + '-' + day + '/' + clip)

   return Response(readStream(f), mimetype='multipart/x-mixed-replace; boundary=frame')    

if __name__ == "__main__":
    app.run(debug=True)
