import sys
from django.contrib.auth import authenticate
from django.contrib.auth import get_user_model
from polls.models import Statistics
from polls.views import *

User = get_user_model()
HOURS_IN_DAY = 24

import random
import datetime
import time
from random import randint
from time import gmtime, strftime
from math import floor,radians,cos, sin, asin, sqrt
NUM_OF_COORDINATES = 500
MAX_RED = 35
MAX_YELLOW = 20 
MAX_GREEN = 15

loads = []
lats = []
lngs = []
center_lat = None
center_lng = None

calculate_environment_average

def setDizingoffCenter():
	global center_lat
	global center_lng
	
	center_lat = 32.075477
	center_lng = 34.77573039999993


def setAzrieliCenter():
	global center_lat
	global center_lng
	
	center_lat = 32.0740769
	center_lng = 34.7922028

def setStateSquere():
	global center_lat
	global center_lng

	center_lat = 32.08651969
	center_lng = 34.7898066


def createDizingoffCoors():
	rightUpLat = 32.09071916431268
	rightUpLng = 34.7911262512207

	leftDownLat = 32.0664286442665
	leftDownLng = 34.76898193359375

	for j in range(0,NUM_OF_COORDINATES):
		lats.append(random.uniform(leftDownLat,rightUpLat))
		lngs.append(random.uniform(leftDownLng,rightUpLng))


def createAzrieliCoors():
	rightUpLat = 32.0799565
	rightUpLng = 34.80395794

	leftDownLat = 32.0692653
	leftDownLng = 34.78438854

	for j in range(0,NUM_OF_COORDINATES):
		lats.append(random.uniform(leftDownLat,rightUpLat))
		lngs.append(random.uniform(leftDownLng,rightUpLng))



def createStateSquereCoors():
	rightUpLat = 32.08948298
	rightUpLng = 34.79422688

	leftDownLat = 32.08261092
	leftDownLng = 34.78124499

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

# def calculate_distance(lat1, lon1, lat2, lon2):
#     """
#     Calculate the great circle distance between two points 
#     on the earth (specified in decimal degrees)
#     """
#     # convert decimal degrees to radians 
#     lon1, lat1, lon2, lat2  = map(radians, [lon1, lat1, lon2, lat2])
#     # haversine formula 
#     dlon = lon2 - lon1 
#     dlat = lat2 - lat1 
#     a = sin(dlat/2)**2 + cos(lat1) * cos(lat2) * sin(dlon/2)**2
#     c = 2 * asin(sqrt(a)) 
#     # Radius of earth in kilometers is 6371
#     m = 6371* c*1000
#     return m

# def calculate_actual_rating(spot_stat):
# 	'''
# 		update rank for new statistics object: spot_stat
# 	'''
# 	spot_rating = float(spot_stat.rating)

# 	stat_rating = ((1-OLD_RANK_WEIGHT) * spot_rating) + (OLD_RANK_WEIGHT * float(calculate_environment_average(spot_stat)))
# 	spot_stat.rating = stat_rating
# 	spot_stat.save()



def createStats():
	cnt_red = 0
	cnt_yellow = 0
	cnt_green = 0
	#for each hour in the day create points according to the load in this hour
	# print("diana")
	# print(HOURS_IN_DAY)
	#for i in range(0,HOURS_IN_DAY):
	for i in range(2,4):

		# create random coordinates in Tel Aviv
		numOfStats= NUM_OF_COORDINATES*loads[i]
		# l = []
		# print "gal", l
		# print("adding points: " + str(numOfStats) + ", hour:" + str(i))
		for j in range(0,int(numOfStats)):
			if j%100 ==0:
				print("j%100 =:" + str(j))
			given_parking_time = strftime("%Y-%m-%d %H:%M:%S", time.localtime())
			dist = calculate_distance(lats[j],lngs[j],center_lat, center_lng)
		#	l.append(dist)
			#calc_rating = dist_to_parking_rate(dist)
			calc_rating = 0

			if (dist < 400):
				# if (cnt_red >= MAX_RED):
				# 	continue
				cnt_red += 1 
				calc_rating = 0
			
			elif (400 <=dist < 750): 
				# if (cnt_yellow >= MAX_YELLOW):
				# 	continue
				cnt_yellow += 1 	
				calc_rating = 0.4

			elif(750 <=dist < 1000):
				# if (cnt_green >= MAX_GREEN):
				# 	continue
				cnt_green += 1 
				calc_rating = 0.8

			else: 
				continue


			# print("lats"+ str(lats[j]))
			# print("lngs"+ str(lngs[j]))
			# print("rating"+ str(calc_rating))
			# print("date"+ str(given_parking_time))
			# print("-------------------------")
			stat = Statistics(lat = lats[j] ,lng= lngs[j],hour = i,rating = calc_rating, date= given_parking_time)
			calculate_actual_rating(stat)
	print("red: " + str(cnt_red) + " yello: " + str(cnt_yellow) + " green: "+ str(cnt_green))

	#print l


# lat1= 32.079265606523364
# lng1= 34.81095314025879

# lat2 = 32.07912015529045
# lng2 = 34.81026649475098

init_loads()
setDizingoffCenter()
#print "Dist: ", calculate_distance(lat1, lng1, ,center_lat, center_lng)
createDizingoffCoors()
createStats()

lats = []
lngs = []
setAzrieliCenter()
createAzrieliCoors()
createStats()

lats = []
lngs = []

setStateSquere()
createStateSquereCoors()
createStats()
