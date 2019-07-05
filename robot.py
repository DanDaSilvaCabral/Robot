#! /usr/bin/python

from picamera import PiCamera
from time import *
import RPi.GPIO as GPIO
from gps import *
from geographiclib.geodesic import Geodesic

def takevid():

	GPIO.setmode(GPIO.BOARD)

	camera = PiCamera()

	camera.resolution = (1024, 768)
	camera.framerate = 15
	with open('/home/pi/Desktop/tests/videos/count', 'r') as f:
		nb = f.read()

	for i in range(6):
		camera.start_preview()
		camera.start_recording('/home/pi/Desktop/tests/videos/video' + nb + str(i) + '.h264')
		nb = int(nb) + 1
		with open('/home/pi/Desktop/tests/videos/count', 'w') as f:
			f.write(str(nb))
		sleep(1800)
		camera.stop_recording()
		camera.stop_preview()


def printGPS():

	gpsd = gps(mode=WATCH_ENABLE|WATCH_NEWSTYLE)
	print 'latitude\tlongitude\ttime utc\t\t\taltitude\tspeed\tclimb' # '\t' = TAB to try and output the data in columns.

	try:
		while True:
			report = gpsd.next() #
		        if report['class'] == 'TPV':

				print getattr(report,'lat',0.0),"\t",
				print getattr(report,'lon',0.0),"\t",
				print getattr(report,'time',''),"\t",
				print getattr(report,'alt','nan'),"\t",
	           		print  getattr(report,'speed','nan'),"\t",
				print getattr(report,'climb','nan'),"\t"
			time.sleep(1)

	except (KeyboardInterrupt, SystemExit): #when you press ctrl+c
		print "Done.\nExiting."


def getGPS():
	gpsd = gps(mode=WATCH_ENABLE|WATCH_NEWSTYLE)
	stop = 0
	while stop != 1:
		report = gpsd.next() #
		if report['class'] == 'TPV':
			cur_coord = {"lat": getattr(report,'lat',0.0), "lon": getattr(report,'lon',0.0), "time": getattr(report, 'time','')}
			stop = 1
			return cur_coord

def get_bearing(lat1, lat2, long1, long2):
	brng = Geodesic.WGS84.Inverse(lat1, long1, lat2, long2)['azi1']
	return brng
