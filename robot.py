#! /usr/bin/python

#This module contains fonctions that I intend to use in a drone (plane, car or boat)
#The GPS capabilities of this module can only work is the gps deamon (gpsd) is running.

from picamera import PiCamera
from time import *
import RPi.GPIO as GPIO
from gps import *
from geographiclib.geodesic import Geodesic
import math


#Here are some image taking functions

def takevid():
	# This function starts recording 6 consecutive videos of 30 minutes (3 hours of recording at most)
	GPIO.setmode(GPIO.BOARD)

	camera = PiCamera()

	try:
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
	except KeyboardInterrupt:
		print "Done. Exiting"

# Some Geolocation functions

def printGPS():
	# This function prints the gps coordinates, time and speed every second
	gpsd = gps(mode=WATCH_ENABLE|WATCH_NEWSTYLE)
	print 'track\tlatitude\tlongitude\ttime utc\t\taltitude\tspeed\tclimb' # '\t' = TAB to try and output the data in columns.

	try:
		while True:
			report = gpsd.next()
		        if report['class'] == 'TPV':
				print getattr(report,'track',0.0),"\t",
				print getattr(report,'lat',0.0),"\t",
				print getattr(report,'lon',0.0),"\t",
				print getattr(report,'time',''),"\t",
				print getattr(report,'alt','nan'),"\t",
	           		print getattr(report,'speed','nan'),"\t",
				print getattr(report,'climb','nan'),"\t"
			time.sleep(1)

	except (KeyboardInterrupt, SystemExit): #when you press ctrl+c
		print "Done.\nExiting."


def getGPS():
	# A function that returns a dictionnary containing the coordinates, time, etc.
	gpsd = gps(mode=WATCH_ENABLE|WATCH_NEWSTYLE)
	stop = 0
	while stop != 1:
		report = gpsd.next() #
		if report['class'] == 'TPV':
			cur_coord = {"bearing": getattr(report,'track',0.0), "lat": getattr(report,'lat',0.0), "lon": getattr(report,'lon',0.0), "time": getattr(report, 'time',''), "alt": getattr(report, 'alt','nan'), "speed": getattr(report, 'speed','nan')}
			stop = 1
			return cur_coord

def get_bearing(lat1, lat2, long1, long2):
	# A function that calculates a direction (+/- 180 degrees) between lat/lon of 2 points
	brng = Geodesic.WGS84.Inverse(lat1, long1, lat2, long2)['azi1']
	return brng

def get_dist(lat1, lat2, long1, long2):
	# A function that calculates a distance (in meters) between lat/lon of 2 points
	dist = Geodesic.WGS84.Inverse(lat1, long1, lat2, long2)['s12']
	return dist


# A few servo motors control functions

def correct_dir(MyPin = 21, tar_lat = 0, tar_lon = 0, sleep = 0.5):

	GPIO.setmode(GPIO.BCM)
	GPIO.setup(MyPin, GPIO.OUT)
	p = GPIO.PWM(MyPin, 50)
	p.start(7.5)

	cur_pos = getGPS()
	try:
		while True:
			time.sleep(sleep)
			new_pos = getGPS()
			if new_pos != cur_pos:
				brng = Geodesic.WGS84.Inverse(cur_pos['lat'], cur_pos['lon'], new_pos['lat'], new_pos['lon'])['azi1']
				dist = Geodesic.WGS84.Inverse(cur_pos['lat'], cur_pos['lon'], new_pos['lat'], new_pos['lon'])['s12']
				targ_brng = Geodesic.WGS84.Inverse(cur_pos['lat'], cur_pos['lon'], tar_lat, tar_lon)['azi1']
				dir = targ_brng - brng
				if dir < -180:
					dir = 360 + dir
				if dir > 180:
					dir = dir - 360
				if int(dist) >= 2 and int(dist) < 5000:
					frq = (float(dir)*5/180)+7.5
					p.ChangeDutyCycle(frq)
					with open('/home/pi/Desktop/Robot/data/record', 'a') as rec:
						rec.write(str(brng)+"\t"+str(dist)+"\t"+str(dir)+"\t"+str(frq)+"\n")
					cur_pos = new_pos

	except (KeyboardInterrupt, SystemExit):
		p.stop()
		GPIO.cleanup()
		print "Done. Exiting."

def head_move(MyPin = 21, frq_min = 2.5, frq_max = 12.5, inter = 0.7):
	# Controls a servo that moves back and forth at a programable frequence and amplitude

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



