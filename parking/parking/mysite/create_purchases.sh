import sys
import random
import datetime
from random import randint
from time import gmtime, strftime
from django.contrib.auth import authenticate
from django.contrib.auth import get_user_model
from polls.models import Purchase
from math import floor
User = get_user_model()

# create users
NUM_OF_USERS = 10
BUYER_NAME = "buyer"
SELLER_NAME = "seller"
PARKING_TIME = 10
DEFAULT_COST = 10
PINCODE_LEN = 6
DUMMY_ADDRESS 	= "dummy address" 	
bNames = []
sNames = []

for i in range(0,NUM_OF_USERS):
	bNames.append(BUYER_NAME+str(i))
	sNames.append(SELLER_NAME+str(i))	

# Tel Aviv coordinates
rightUpLat = 32.088
rightUpLng = 34.818

rightDownLat = 32.056
rightDownLng = 34.815

leftUpLat = 32.09
leftUpLng = 34.774

leftDownLat = 32.057
leftDownLng = 34.766


lats = []
lngs = []

# create random coordinates in Tel Aviv
for i in range(0,NUM_OF_USERS):
	lats.append(random.uniform(leftDownLat,rightUpLat))
	lngs.append(random.uniform(leftDownLng,rightUpLng))

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