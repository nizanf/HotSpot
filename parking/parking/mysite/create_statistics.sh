import sys
from django.contrib.auth import authenticate
from django.contrib.auth import get_user_model
from polls.models import Statistics
#from polls.views import *

User = get_user_model()
HOURS_IN_DAY = 24

import random
import datetime
import time
from random import randint
from time import gmtime, strftime
from math import floor,radians,cos, sin, asin, sqrt
NUM_OF_COORDINATES = 1000

loads = []
lats = []
lngs = []
center_lat = None
center_lng = None


def setTelAvivCenter():
	global center_lat
	global center_lng
	
	center_lat = 32.075477
	center_lng = 34.77573039999993

def createTelAvivCoors():
	rightUpLat = 32.09071916431268
	rightUpLng = 34.7911262512207

	leftDownLat = 32.0664286442665
	leftDownLng = 34.76898193359375

	for j in range(0,NUM_OF_COORDINATES):
		lats.append(random.uniform(leftDownLat,rightUpLat))
		lngs.append(random.uniform(leftDownLng,rightUpLng))

def init_loads():
	#init loads list
	for i in range(0,HOURS_IN_DAY):
		loads.append(0.2)

	for i in range(6,10):
		loads[i] = 0.9

	for i in range(10,14):
		loads[i] = 0.5

	for i in range(14,16):
		loads[i] = 0.8

	for i in range(16,19):
		loads[i] = 1

	for i in range(19,22):
		loads[i] = 0.5

	for i in range(22,HOURS_IN_DAY):
		loads[i] = 0.3

def calculate_distance(lat1, lon1, lat2, lon2):
    """
    Calculate the great circle distance between two points 
    on the earth (specified in decimal degrees)
    """
    # convert decimal degrees to radians 
    lon1, lat1, lon2, lat2  = map(radians, [lon1, lat1, lon2, lat2])
    # haversine formula 
    dlon = lon2 - lon1 
    dlat = lat2 - lat1 
    a = sin(dlat/2)**2 + cos(lat1) * cos(lat2) * sin(dlon/2)**2
    c = 2 * asin(sqrt(a)) 
    # Radius of earth in kilometers is 6371
    m = 6371* c*1000
    return m


def createStats():

	#for each hour in the day create points according to the load in this hour
	# print("diana")
	# print(HOURS_IN_DAY)
	#for i in range(0,HOURS_IN_DAY):
	for i in range(20,22):

		# create random coordinates in Tel Aviv
		numOfStats= NUM_OF_COORDINATES*loads[i]
		l = []
		print "gal", l
		print("adding points: " + str(numOfStats) + ", hour:" + str(i))
		for j in range(0,int(numOfStats)):
			if j%100 ==0:
				print(str(j))
			given_parking_time = strftime("%Y-%m-%d %H:%M:%S", time.localtime())
			dist = calculate_distance(lats[j],lngs[j],center_lat, center_lng)
			l.append(dist)
			#calc_rating = dist_to_parking_rate(dist)
			calc_rating = 0

			if (dist < 800):
				calc_rating = 0
			
			elif (dist < 2000): 
				calc_rating = 0.4
			else: 
				calc_rating = 0.8


			# print("lats"+ str(lats[j]))
			# print("lngs"+ str(lngs[j]))
			# print("rating"+ str(calc_rating))
			# print("date"+ str(given_parking_time))
			# print("-------------------------")
			stat = Statistics(lat = lats[j] ,lng= lngs[j],hour = i,rating = calc_rating, date= given_parking_time)
			stat.save()

	print l


lat1= 32.079265606523364
lng1= 34.81095314025879

lat2 = 32.07912015529045
lng2 = 34.81026649475098

setTelAvivCenter()
#print "Dist: ", calculate_distance(lat1, lng1, ,center_lat, center_lng)
init_loads()
createTelAvivCoors()
createStats()



