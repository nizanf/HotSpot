import sys
import random
import datetime
import json
import time
from random import randint
from time import gmtime, strftime
from django.contrib.auth import authenticate
from django.contrib.auth import get_user_model
from polls.models import Purchase,FreeSpot
from math import floor
User = get_user_model()

# create users
NUM_OF_USERS = 10
NUM_OF_FREE_SPOTS = 10
NUM_OF_PURCHASES = 10
PARKING_TIME = 10
DEFAULT_COST = 10

BUYER_NAME = "buyer"
SELLER_NAME = "seller"
DUMMY_ADDRESS 	= "dummy address" 	
PINCODE_LEN = 6


center_lat = None
center_lng = None

bNames = []
sNames = []
lats = []
lngs = []


def setUsers():
	for i in range(0,NUM_OF_USERS):
		bNames.append(BUYER_NAME+str(i))
		sNames.append(SELLER_NAME+str(i))	


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

	for j in range(0,NUM_OF_PURCHASES):
		lats.append(random.uniform(leftDownLat,rightUpLat))
		lngs.append(random.uniform(leftDownLng,rightUpLng))


def createPurchases():

	# create random coordinates in Tel Aviv
	for i in range(0,NUM_OF_USERS):

		seller 					= User.objects.get(username=sNames[i])
		seller_rating 			= seller.profile.rating
		wanted_prking_time		= int(PARKING_TIME)
		now 					= datetime.datetime.now()
		time_delta 				= now + datetime.timedelta(minutes = wanted_prking_time)

		#create new Purchase
		given_parking_time 		= strftime("%Y-%m-%d %H:%M:%S", time_delta.timetuple())
		pincode 				= ''.join(["%s" % randint(0, 9) for num in range(0, PINCODE_LEN)])
		cost_value 				= DEFAULT_COST #+ floor(seller_rating)
		purchase 				= Purchase(seller_id = seller.pk,\
								 cost = cost_value, parking_address = DUMMY_ADDRESS,\
								  parking_time = given_parking_time,\
								   parking_address_lat = lats[i], \
									parking_address_lng = lngs[i], pin_code = pincode)
		purchase.save()
	#	print("created purchases ids" + str(purchase.pk))


def createRandomFreeSpots():

	for i in range(0,NUM_OF_FREE_SPOTS):
		user_index   = random.randint(0,NUM_OF_USERS-1)
		#print(user_index)
		reporter 	 = User.objects.get(username=sNames[user_index])

		given_parking_time = strftime("%Y-%m-%d %H:%M:%S", time.localtime())
		#create new freeSpot 
		free_parking = FreeSpot(reporters_ids = json.dumps([reporter.pk]), last_report_time = given_parking_time,
			 						parking_address = DUMMY_ADDRESS, street_name = DUMMY_ADDRESS, 	
			 						parking_address_lat = lats[i], parking_address_lng = lngs[i], 
									parking_rank = reporter.profile.rating)
		free_parking.is_verified = 1
		free_parking.save()


setUsers()
setTelAvivCenter()
createTelAvivCoors()
createPurchases()
createRandomFreeSpots()
