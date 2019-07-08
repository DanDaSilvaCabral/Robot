#! /usr/bin/python

from picamera import PiCamera
from time import *
import RPi.GPIO as GPIO
from gps import *
from geographiclib.geodesic import Geodesic
import math

def takevid():

	GPIO.setmode(GPIO.BOARD)

	camera = PiCamera()

	camera.resolution = (1920, 1080)
	camera.framerate = 15
	with open('/home/pi/Desktop/Robot/data/videos/count', 'r') as f:
		nb = f.read()

	for i in range(6):
		camera.start_preview()
		camera.start_recording('/home/pi/Desktop/Robot/data/videos/video' + nb + str(i) + '.h264')
		nb = int(nb) + 1
		with open('/home/pi/Desktop/Robot/data/videos/count', 'w') as f:
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
			#	print getattr(report,'alt','nan'),"\t",
	           		print  getattr(report,'speed','nan'),"\t",
			#	print getattr(report,'climb','nan'),"\t"
			time.sleep(1)

	except (KeyboardInterrupt, SystemExit): #when you press ctrl+c
		print "Done.\nExiting."


def getGPS():
	gpsd = gps(mode=WATCH_ENABLE|WATCH_NEWSTYLE)
	stop = 0
	while stop != 1:
		report = gpsd.next() #
		if report['class'] == 'TPV':
			cur_coord = {"lat": getattr(report,'lat',0.0), "lon": getattr(report,'lon',0.0), "time": getattr(report, 'time',''), "alt": getattr(report, 'alt','nan'), "speed": getattr(report, 'speed','nan')}
			stop = 1
			return cur_coord

def get_bearing(lat1, lat2, long1, long2):
	brng = Geodesic.WGS84.Inverse(lat1, long1, lat2, long2)['azi1']
	return brng

def get_dist(lat1, lat2, long1, long2):
	dist = Geodesic.WGS84.Inverse(lat1, long1, lat2, long2)['s12']
	return dist

def cur_bearing(targ_lat = 43.7, targ_lon = 7.26):
	cur_pos = getGPS()
	try:
		while True:
			time.sleep(1)
			new_pos = getGPS()
			if new_pos != cur_pos:
				brng = get_bearing(cur_pos['lat'], new_pos['lat'], cur_pos['lon'], new_pos['lon'])
				dist = get_dist(cur_pos['lat'], new_pos['lat'], cur_pos['lon'], new_pos['lon'])
				targ_brng = get_bearing(new_pos['lat'], targ_lat, new_pos['lon'], targ_lon)
				dir = int(targ_brng) - int(brng)
				if int(dist) > 3 and int(dist) < 5000:
					with open('/home/pi/Desktop/Robot/data/record', 'a') as rec:
						rec.write(str(brng)+'\t'+str(dist)+'\t'+str(dir)+'\n')
					cur_pos = new_pos
	except (KeyboardInterrupt, SystemExit):
		print "Done.\nExiting."


def head_move(MyPin = 21, frq_min = 2.5, frq_max = 12.5, inter = 0.7):
	GPIO.setmode(GPIO.BCM)
	GPIO.setup(MyPin, GPIO.OUT)

	p = GPIO.PWM(MyPin, 50)
	p.start(frq_min)
	time.sleep(inter)
	try:
		while True:
			p.ChangeDutyCycle(frq_max)
			time.sleep(inter)
			p.ChangeDutyCycle(frq_min)
			time.sleep(inter)

	except KeyboardInterrupt:
		p.stop()
		GPIO.cleanup()
