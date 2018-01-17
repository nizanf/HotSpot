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
NUM_OF_COORDINATES = 1000
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


def setNamirCenter():
	global center_lat
	global center_lng
	
	center_lat = 32.1101178
	center_lng = 34.792159

def createNamirCoors():
	rightUpLat = 32.11311308
	rightUpLng = 34.79910851

	leftDownLat = 32.10148056
	leftDownLng = 32.10148056

	for j in range(0,NUM_OF_COORDINATES):
		lats.append(random.uniform(leftDownLat,rightUpLat))
		lngs.append(random.uniform(leftDownLng,rightUpLng))		

def setHofMetzitzimCenter():
	global center_lat
	global center_lng
	
	center_lat = 32.09362778
	center_lng = 34.77747917

def createHofMetzitzimCoors():
	rightUpLat = 32.09420949
	rightUpLng = 34.78177071

	leftDownLat = 32.08810133
	leftDownLng = 34.77147102

	for j in range(0,NUM_OF_COORDINATES):
		lats.append(random.uniform(leftDownLat,rightUpLat))
		lngs.append(random.uniform(leftDownLng,rightUpLng))		


def setSederotBenGurionCenter():
	global center_lat
	global center_lng
	
	center_lat = 32.08868308
	center_lng = 34.77747917

def creatSederotBenGurionCoors():
	rightUpLat = 32.0925007
	rightUpLng = 34.78350878

	leftDownLat = 32.0875923
	leftDownLng = 34.77136374

	for j in range(0,NUM_OF_COORDINATES):
		lats.append(random.uniform(leftDownLat,rightUpLat))
		lngs.append(random.uniform(leftDownLng,rightUpLng))		


def setGivatAmalCenter():
	global center_lat
	global center_lng
	
	center_lat = 32.09348235
	center_lng = 34.7988081

def creatGivatAmalCoors():
	rightUpLat = 32.11951034
	rightUpLng = 34.82095242

	leftDownLat = 32.09202805
	leftDownLng = 34.79391575

	for j in range(0,NUM_OF_COORDINATES):
		lats.append(random.uniform(leftDownLat,rightUpLat))
		lngs.append(random.uniform(leftDownLng,rightUpLng))	

	cnt_red = 0
	cnt_yellow = 0
	cnt_green = 0
	#for i in range(3,5):
	for i in range(0,HOURS_IN_DAY):
		print("start hour:" str(i))

		# create random coordinates in Tel Aviv
		numOfStats= NUM_OF_COORDINATES*loads[i]

		for j in range(0,int(numOfStats)):
			if j%100 ==0:
				print("j%100 =:" + str(j))
			given_parking_time = strftime("%Y-%m-%d %H:%M:%S", time.localtime())
			dist = calculate_distance(lats[j],lngs[j],center_lat, center_lng)
		#	l.append(dist)
			#calc_rating = dist_to_parking_rate(dist)
			calc_rating = 0

			if (dist < 600):
				# if (cnt_red >= MAX_RED):
				# 	continue
				cnt_red += 1 
				calc_rating = 0
			
			elif (600 <=dist < 1200): 
				# if (cnt_yellow >= MAX_YELLOW):
				# 	continue
				cnt_yellow += 1 	
				calc_rating = 0.4

			elif(1200 <=dist < 2000):
				# if (cnt_green >= MAX_GREEN):
				# 	continue
				cnt_green += 1 
				calc_rating = 0.8

			else: 
				continue
			stat = Statistics(lat = lats[j] ,lng= lngs[j],hour = i,rating = calc_rating, date= given_parking_time)
			#calculate_actual_rating(stat)
			stat.save()
	print("red: " + str(cnt_red) + " yello: " + str(cnt_yellow) + " green: "+ str(cnt_green))	




def setRokachCenter():
	global center_lat
	global center_lng
	
	center_lat = 32.10046265
	center_lng = 34.79123354

def creatRokachCoors():
	rightUpLat = 32.10500683
	rightUpLng = 34.79827166

	leftDownLat = 32.09315513
	leftDownLng = 34.78067636

	for j in range(0,NUM_OF_COORDINATES):
		lats.append(random.uniform(leftDownLat,rightUpLat))
		lngs.append(random.uniform(leftDownLng,rightUpLng))	

	cnt_red = 0
	cnt_yellow = 0
	cnt_green = 0
	#for i in range(3,5):
	for i in range(0,HOURS_IN_DAY):
		print("start hour:" str(i))
		# create random coordinates in Tel Aviv
		numOfStats= NUM_OF_COORDINATES*loads[i]

		for j in range(0,int(numOfStats)):
			if j%100 ==0:
				print("j%100 =:" + str(j))
			given_parking_time = strftime("%Y-%m-%d %H:%M:%S", time.localtime())
			dist = calculate_distance(lats[j],lngs[j],center_lat, center_lng)
		#	l.append(dist)
			#calc_rating = dist_to_parking_rate(dist)
			calc_rating = 0

			if (dist < 600):
				# if (cnt_red >= MAX_RED):
				# 	continue
				cnt_red += 1 
				calc_rating = 0
			
			elif (600 <=dist < 1200): 
				# if (cnt_yellow >= MAX_YELLOW):
				# 	continue
				cnt_yellow += 1 	
				calc_rating = 0.4

			elif(1200 <=dist < 2000):
				# if (cnt_green >= MAX_GREEN):
				# 	continue
				cnt_green += 1 
				calc_rating = 0.8

			else: 
				continue
			stat = Statistics(lat = lats[j] ,lng= lngs[j],hour = i,rating = calc_rating, date= given_parking_time)
			#calculate_actual_rating(stat)
			stat.save()
	print("red: " + str(cnt_red) + " yello: " + str(cnt_yellow) + " green: "+ str(cnt_green))	






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


def createStats():
	cnt_red = 0
	cnt_yellow = 0
	cnt_green = 0
	#for each hour in the day create points according to the load in this hour
	# print("diana")
	# print(HOURS_IN_DAY)
	for i in range(0,HOURS_IN_DAY):
	#for i in range(3,5):
		print("start hour:" str(i))
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
			
			elif (400 <=dist < 800): 
				# if (cnt_yellow >= MAX_YELLOW):
				# 	continue
				cnt_yellow += 1 	
				calc_rating = 0.4

			elif(800 <=dist < 1250):
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
		#	calculate_actual_rating(stat)
			stat.save()
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

lats = []
lngs = []
setNamirCenter()
createNamirCoors()
createStats()


lats = []
lngs = []
setHofMetzitzimCenter()
createHofMetzitzimCoors()
createStats()


lats = []
lngs = []

setSederotBenGurionCenter()
creatSederotBenGurionCoors()
createStats()

lats = []
lngs = []

setGivatAmalCenter()
creatGivatAmalCoors()

lats = []
lngs = []
setRokachCenter()
creatRokachCoors()