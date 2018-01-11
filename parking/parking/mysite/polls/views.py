# -*- coding: utf-8 -*-
from __future__ import unicode_literals

import datetime
# for lock 
import threading
import time

from django.shortcuts import render
from django.http import HttpResponse
from django.template import loader
from django.contrib.auth.models import User
from .models import Profile, Purchase, FreeSpot, Statistics
from django.core import serializers
from random import randint
import json
from time import gmtime, strftime
from django.contrib.auth import authenticate, login, logout
from django.http import JsonResponse
from math import radians, cos, sin, asin, sqrt
from decimal import *

DEFAULT_PARKING_RATE = 2
MIN_POINTS = 0 
TIMEOUT_RELOGIN = 10
TIMEOUT_LOCK = 10
TIMEOUT_AVAILABLE_PARKING = 20
THRESHOLD_FAILURES = 5
THRESHOLD_RATING_TO_FREE_SPOT = -1
THRESHOLD_RELEVANT_PARKING_TIME_DIFF = 5000
FREE_PARKING_EXISTENCE_TIME = 40
FREE_PARKING_RATING_REWARD = 1.1
FREE_PARKING_POINTS_REWARD = 2
MAX_POINTS = 1000000
MAX_RATING = 5
PINCODE_LEN = 6
OLD_RANK_WEIGHT = 0.25
COLOR_THRESHOLD = 0.5
NUMBER_OF_DAYS_FOR_STATISTICS = 7
MINUTES_IN_HOUR = 60
HOURS_IN_DAY = 24
DAYS_IN_WEEK = 7
HOURS_IN_WEEK = HOURS_IN_DAY * DAYS_IN_WEEK

RED = 0		# Busy spot
GREEN = 1 	# Available spot



DIST_HIGH_BOUND_RATE_2 = 1000
DIST_HIGH_BOUND_RATE_3 = 500
DIST_HIGH_BOUND_RATE_4 = 200
DIST_HIGH_BOUND_RATE_5 = 100


class ParkingStatus:
	DONE = 'done'
	EXPIRED = 'expired'
	CANCELED = 'canceled'
	IN_PROCESS = 'in process'
	AVAILABLE = 'available'


def call_login(request):
	return render(request, 'polls/login.html')

def call_homepage(request):

	update_user_spots_status (request.user.pk)
	return render(request, 'polls/hotspot.html')

def call_register(request):
	update_user_spots_status (request.user.pk)
	return render(request, 'polls/register.html')

def call_report(request):
	update_user_spots_status (request.user.pk)
	return render(request, 'polls/report_parking.html')

def call_find(request):
	update_user_spots_status (request.user.pk)
	return render(request, 'polls/find_parking.html')

def call_heatmap(request):
	update_user_spots_status (request.user.pk)
	points = get_statistics_color_classification()
	return render(request, 'polls/heatmap.html', {'points':points})

def checkIfActivityValid(request):

	update_user_spots_status (request.user.pk)

	sell_purchase = Purchase.objects.filter(seller_id = request.user.pk)
	max_pk = 0
	last_activity = None
	buy_purchase = Purchase.objects.filter(buyer_id = request.user.pk)
	
	all_purchase = list(sell_purchase)  +list(buy_purchase)

	for purchase in all_purchase:
		if ("Binyamin mi-Tudela St 1" in purchase.parking_address):
			print(" Binyamin pk = "+str(purchase.pk))
		if ("Dr Haim Brody St 12" in purchase.parking_address):
			print(" Dr Haim pk = "+str(purchase.pk))

		if (purchase.pk > max_pk):
			max_pk = purchase.pk
			last_activity = purchase

	if last_activity == None:
		return False

	if last_activity.status == ParkingStatus.AVAILABLE or last_activity.status == ParkingStatus.IN_PROCESS:
		return True
	return False
	

def call_last_activity(request):

	update_user_spots_status (request.user.pk)

	sell_purchase = Purchase.objects.filter(seller_id = request.user.pk)
	max_pk = 0
	last_activity = None
	buy_purchase = Purchase.objects.filter(buyer_id = request.user.pk)
	
	all_purchase = list(sell_purchase)  +list(buy_purchase)



	for purchase in all_purchase:

		if (purchase.pk > max_pk):
			max_pk = purchase.pk
			last_activity = purchase


	if (last_activity == None):
		last_activity = ["", "", "", "", "", "", "", "-1"]

		return render(request, 'polls/last_activity.html', {'last_activity':last_activity }) 
		
	if (minutes_elapsed(last_activity.parking_time) > 0 and last_activity.status != ParkingStatus.DONE and last_activity.status != ParkingStatus.CANCELED):
		last_activity.status = ParkingStatus.EXPIRED
		last_activity.save()

	seller_username = (User.objects.get(pk = last_activity.seller_id)).username

	if (last_activity.buyer_id == -1):
		buyer_username = "--"
		contact = "--"
	else:
		buyer_username = (User.objects.get(pk = last_activity.buyer_id)).username
		contact = (User.objects.get(pk = last_activity.buyer_id)).profile.phone_number

	if (last_activity.seller_id == request.user.pk):
		seller_username = "Me"
		pincode = ""
	else:
		buyer_username = "Me"
		contact = (User.objects.get(pk = last_activity.seller_id)).profile.phone_number
		pincode = last_activity.pin_code

	last_activity = [buyer_username, seller_username, last_activity.parking_time, last_activity.status, last_activity.parking_address, contact, pincode, last_activity.pk]

	return render(request, 'polls/last_activity.html', {'last_activity':last_activity }) 
	



def aut_pincode(request):

	pincode = request.POST.get("pincode")
	purchase_id = int(request.POST.get("purchase_id"))
	
	purchase = Purchase.objects.get(pk = purchase_id)

	print("our pincode = "+str(pincode)+" type = "+str(type(pincode)))

	print("right pincode = "+str(purchase.pin_code)+" type = "+str(type(purchase.pin_code)))


	if (str(pincode) == purchase.pin_code ):

		purchase.status = ParkingStatus.DONE
		purchase.save()

		seller_id = int(purchase.seller_id)
		
		seller = User.objects.get(pk = seller_id)
		seller.profile.points += purchase.cost

		seller.profile.rating = seller.profile.rating * 1.1

		if (seller.profile.rating == 0):
			seller.profile.rating = 0.1

		seller.save()

		data = {'msg': "Pincode correct!"}

	else:
	
		
		data = {'msg': "Pincode incorrect!"}
	return JsonResponse(data)
		


	


def call_history(request):

	sell_purchase = Purchase.objects.filter(seller_id = request.user.pk)
	buy_purchase = Purchase.objects.filter(buyer_id = request.user.pk)
	all_free_spot = FreeSpot.objects.all()
	
	update_user_spots_status (request.user.pk)


	free_spot = []	

	for spot in all_free_spot:

		reporters_ids_list = json.loads(spot.reporters_ids)
		if request.user.pk in reporters_ids_list:
			free_spot.append(spot)

	all_history = list(sell_purchase) + list(buy_purchase) + list(free_spot)


	all_history.sort(key=lambda x: datetime.datetime.strptime(x.parking_time, "%Y-%m-%d %H:%M:%S") if x.class_name() == "Purchase" else datetime.datetime.strptime(x.last_report_time, "%Y-%m-%d %H:%M:%S"), reverse=True)


	history_as_table = []

	for element in all_history:
		address = element.parking_address

		if element.class_name() == "Purchase":
			elemnt_type = "Purchase"
			status = element.status
			date_and_time = element.parking_time
			if (element.seller_id == request.user.pk):
				if (element.buyer_id == -1):
					buyer_username = "--"
				else:
					buyer_username = User.objects.get(pk = element.buyer_id).username
				seller_username = "Me"
			else:
				if (element.seller_id == -1):
					seller_username = "--"
				else:
					seller_username = User.objects.get(pk = element.seller_id).username
				buyer_username = "Me"
				
		else:
			elemnt_type = "Report"
			date_and_time = element.last_report_time
			buyer_username = "N/A"
			seller_username = "Me"
			status = "N/A"

		current_row = [elemnt_type, address, date_and_time, buyer_username, seller_username, status]
		history_as_table.append(current_row)

	return render(request, 'polls/history.html', {'history_as_table':history_as_table})


def call_offer(request):
	return render(request, 'polls/offer_parking.html')


def login_user(request):
	request.session["msg"] = ""

	"""
		Login method
	"""
	if ('login_failures' in request.session and 
		request.session['login_failures'] >= THRESHOLD_FAILURES and 
		minutes_elapsed(request.session['last_failure']) < TIMEOUT_RELOGIN ):

			request.session['msg'] = str("The user is locked for {0} minutes".format(TIMEOUT_RELOGIN))

			return render(request, 'polls/is_login.html', {"is_login":"false"})


	given_username = request.POST.get("username")
	print("given_username = "+given_username)
	given_password = request.POST.get("password")
	print("given_password = "+given_password)
	user = authenticate(username=given_username, password=given_password)

	# found user
	if user : 

		# If user is banned
	  	if (user.profile.is_blocked):
			request.session['msg'] = "User is blocked!"
	  		return render(request, 'polls/is_login.html', {"is_login":"false"})
	  	
	  	# Success
		login(request, user)
		
	  	request.session['login_failures'] = 0
	  	request.session['query'] = "0"
	  	request.session['last_failure'] = None
		return render(request, 'polls/is_login.html', {"is_login":"true"})
	

	else: # login failed	
		print("failed")
		request.session['login_failures'] = request.session['login_failures'] + 1 if 'login_failures' in request.session else 1
		print("\n\n\n " + str(time.localtime()) + " \n\n\n")
		request.session['last_failure'] = strftime("%Y-%m-%d %H:%M:%S", time.localtime())
	  	request.session["msg"] = "username or password incorrect!"
	  	return render(request, 'polls/is_login.html', {"is_login":"false"})


def minutes_elapsed(last_failure_in_string):
	"""
		Return True if user is still in timeout
	"""

	last_failure_in_datetime = datetime.datetime.strptime(last_failure_in_string, "%Y-%m-%d %H:%M:%S")
	diff = (datetime.datetime.now() - last_failure_in_datetime)

	return (diff.total_seconds() / 60)


def register(request):
	"""
		Register method
	"""
	request.session["msg"] = ""

	given_username 		= request.POST.get("username") 		# in template, div name = username.
	given_first_name 	= request.POST.get("first_name") 	# in template, div name = first_name.
	given_last_name 	= request.POST.get("last_name") 	# in template, div name = last_name.
	given_email 		= request.POST.get("email") 		# in template, div name = email.
	given_password	 	= request.POST.get("password") 		# in template, div name = password.
	given_phone_number 	= request.POST.get("phone_number") 	# in template, div name = phone_number.

	# Unique username, mail and email check

	users_list_by_username = User.objects.filter(username = given_username)
	if (users_list_by_username): #there is a user with this username

		request.session["msg"] = "This username already exists"
		return render(request, 'polls/register.html', {})

	users_list_by_phone = Profile.objects.filter(phone_number = given_phone_number)
	if (users_list_by_phone): #there is a user with this phone number

		request.session["msg"] = "This phone number already exists"
		return render(request, 'polls/register.html', {})

	users_list_by_email	= User.objects.filter(email = given_email)
	if (users_list_by_email): #there is a user with this username

		request.session["msg"] = "This email already exists"
		return render(request, 'polls/register.html', {})


	new_user = User.objects.create_user(username=given_username, \
	 		password = given_password, email = given_email, \
	 		first_name = given_first_name, last_name = given_last_name)

	new_user.profile.phone_number = given_phone_number
	new_user.save()
 	
	return render(request, 'polls/is_register.html', {"is_register":"true"})


def logout_user(request):
	update_user_spots_status (request.user.pk)
	"""	
		Logout method
	"""
	logout(request)
	return render(request, 'polls/login.html')

def extract_street_name(parking_address):
	if (" St " in parking_address):
		return parking_address.split(" St ")[0]
	else:
		return parking_address.split(",")[0]

def report_free_parking(request):
	update_user_spots_status (request.user.pk)
	print("here1")
	given_lat = float(request.POST.get("lat_address"))
	given_lng = float(request.POST.get("lng_address"))
	
	request.session["msg"] = ""

	given_parking_address 		= request.POST.get("address") 	

	given_parking_time = strftime("%Y-%m-%d %H:%M:%S", time.localtime())
	given_reporter_id 		= request.user.pk 


	given_street_name = extract_street_name(given_parking_address)

	# Get all parking in the street
	parking_in_street = FreeSpot.objects.filter(street_name=given_street_name)


	found_valid_parking = False

	if parking_in_street:
		print("here1")

		for parking in parking_in_street:
			
			diff_time = minutes_elapsed(parking.last_report_time)

			# If the parking is still relvent
			if diff_time < FREE_PARKING_EXISTENCE_TIME:

				found_valid_parking = True

				reporters_ids_json = parking.reporters_ids
				reporters_ids_list = json.loads(reporters_ids_json)
				
				if (given_reporter_id in reporters_ids_list):
					break

				reporters_ids_list.append(given_reporter_id)
				reporters_ids_json = json.dumps(reporters_ids_list)
				parking.reporters_ids = reporters_ids_json
				parking.parking_rank += request.user.profile.rating

				# If there is enough rating of reporters to verify
				# the parking
				print ("parking.is_verified = "+str(parking.is_verified))
				if parking.is_verified:
					# Update rank/points to given_reporter_id user
					reporter_user = User.objects.get(pk=given_reporter_id)
					update_rating_for_user(reporter_user,'report')
						

				# If the parking rank is over the threshold - add points to 
				# the reporters and show it in the map
				else: 
					print("parking.parking_rank = "+str(parking.parking_rank))
					print("THRESHOLD_RATING_TO_FREE_SPOT = "+str(THRESHOLD_RATING_TO_FREE_SPOT))
					if (parking.parking_rank >= THRESHOLD_RATING_TO_FREE_SPOT):
						now = datetime.datetime.now()
						parking.is_verified = 1
						stat = Statistics( lat = parking_address_lat ,lng= parking_address_lng,hour =  int(now.hour),rating =GREEN, date=given_parking_time)
						print("statistics created")


						calculate_actual_rating(stat)
						for user_id in reporters_ids_list:
							# Update rank/points to given_reporter_id user
							reporter_user = User.objects.get(pk=user_id)
							update_rating_for_user(reporter_user,'report')
							

				parking.save()
				break


	# If we did not find the parking - add to the list
	if not found_valid_parking:
		free_parking = FreeSpot(reporters_ids = json.dumps([given_reporter_id]), last_report_time = given_parking_time,
		 						parking_address = given_parking_address, street_name = given_street_name, 	
		 						parking_address_lat = given_lat, parking_address_lng = given_lng, 
								parking_rank = request.user.profile.rating)

		reporters_ids_json = free_parking.reporters_ids
		reporters_ids_list = json.loads(reporters_ids_json)

		reporters_ids_list.append(given_reporter_id)
		reporters_ids_json = json.dumps(reporters_ids_list)
		free_parking.reporters_ids = reporters_ids_json
		free_parking.parking_rank += request.user.profile.rating


		if (free_parking.parking_rank >= THRESHOLD_RATING_TO_FREE_SPOT):
			now = datetime.datetime.now()
			free_parking.is_verified = 1
			stat = Statistics( lat = given_lat ,lng= given_lng, hour =  int(now.hour),rating =GREEN, date=given_parking_time)
			print("statistics created")


			print ("before = "+str(stat.rating))

			calculate_actual_rating(stat)
			print ("after = "+str(stat.rating))




			for user_id in reporters_ids_list:
				# Update rank/points to given_reporter_id user
				reporter_user = User.objects.get(pk=user_id)
				update_rating_for_user(reporter_user,'report')

		free_parking.save()




	return render(request, 'polls/hotspot.html')


def clear_msg(request):
   	if request.is_ajax() and request.method=='POST':
   		print(request.session['msg'])

        request.session['msg'] = "" 
        print(request.session['msg'])
        return HttpResponse("cleared message")



def user_query(request):
	request.session['query'] = "1"

	if request.is_ajax() and request.method=='POST':
   		rating = request.POST.get("ret")
   		try:
   			rating_int = int(rating) 
   			if (rating_int<1 or rating_int > 10):
   				return HttpResponse("invalid rating")
			else:
				rating = float(rating_int)/10
		except:
			return HttpResponse("invalid rating")


		user = User.object.get(pk = request.user.pk)

		user.profile.points += 1

		user.save()

		print(rating)

		parking_time = strftime("%Y-%m-%d %H:%M:%S", time.localtime())

   		user_lat = request.POST.get("user_lat")
   		user_lng = request.POST.get("user_lng")
   		print(user_lng)
   		print(user_lat)
   		now = datetime.datetime.now()
   		stat = Statistics( lat = user_lat,lng= user_lng, hour = int(now.hour),rating =rating, date=parking_time)			
		calculate_actual_rating(stat)


        return HttpResponse("statistics created")



def update_user_spots_status(user_id):
	sell_spot_list = Purchase.objects.filter(seller_id = user_id)
	buy_spot_list  = Purchase.objects.filter(buyer_id = user_id)

	all_user_spot = list(sell_spot_list) + list(buy_spot_list)

	for spot in all_user_spot:
		if (spot.status == ParkingStatus.AVAILABLE or spot.status == ParkingStatus.IN_PROCESS):
			
			if (minutes_elapsed(spot.parking_time) > 0):
				
				spot.status = ParkingStatus.EXPIRED
				print(ParkingStatus.EXPIRED)
				spot.save()




def offer_new_parking(request):
	valid_activity = checkIfActivityValid(request)
	if (valid_activity == True):
		request.session["msg"] = "You still have valid activity! End or cancel last activily to create new activity"
		return render(request, 'polls/hotspot.html')

	given_lat = request.POST.get("lat_address")
	given_lng = request.POST.get("lng_address")
	
	request.session["msg"] = ""

	given_seller_id 		= int(request.user.pk)  

	update_user_spots_status(given_seller_id)

	if (Purchase.objects.filter(seller_id = given_seller_id, status = ParkingStatus.AVAILABLE) or Purchase.objects.filter(seller_id = given_seller_id, status = ParkingStatus.IN_PROCESS)):
		request.session["msg"] = "You already submitted a parking!!!"
		return render(request, 'polls/hotspot.html')


	given_parking_address 		= request.POST.get("address") 	

	given_parking_time_in_minutes	= int(request.POST.get("time"))

	now = datetime.datetime.now()
	time_delta = now + datetime.timedelta(minutes = given_parking_time_in_minutes)

	given_parking_time = strftime("%Y-%m-%d %H:%M:%S", time_delta.timetuple())





	pincode = ''.join(["%s" % randint(0, 9) for num in range(0, PINCODE_LEN)])


	purchase 			= Purchase(seller_id = given_seller_id, parking_address = given_parking_address, parking_time = given_parking_time, parking_address_lat = given_lat, parking_address_lng = given_lng, pin_code = pincode)

	purchase.save()

	return render(request, 'polls/hotspot.html')




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


def update_spots_on_map(request):

	lat = float(request.POST.get('lat'))


	if (not lat): 
		lat = float(32.121678)

	lng = float(request.POST.get('lng'))
	if (not lng):
		lat = float(34.791143)

	radius = float(request.POST.get('radius'))
	if (not radius): 
		radius = 100

	given_parking_time_in_minutes = int(request.POST.get('minutes'))
	now = datetime.datetime.now()
	time_delta = now + datetime.timedelta(minutes = given_parking_time_in_minutes)
	given_parking_time = strftime("%Y-%m-%d %H:%M:%S", time_delta.timetuple())
	
	relevant_parkings 	= get_parkings_by_radius(lat, lng, radius, given_parking_time)
	
	relv_park = json.loads(relevant_parkings)
	for p in relv_park:
		seller_id = p['fields']['seller_id']
		seller_user = Profile.objects.get(pk=seller_id)
		p['fields']['seller_name'] = seller_user.user.username
		p['fields']['seller_rating'] = seller_user.rating
		print "====================="
		print p
		print "====================="
		print relv_park
		print "====================="
	
	relevant_free_parkings 	= get_free_parkings_by_radius(lat, lng, radius, given_parking_time)

	data = {'relevant_parkings': relv_park, 'relevant_free_parkings': relevant_free_parkings}
	print "\n\n\n\n\n"
	print data
	print "\n\n"

	return JsonResponse(data)


def get_free_parkings_by_radius(lat1, lng1, radius, parking_time):
	
	all_parkings = FreeSpot.objects.filter(is_verified=1)
 	relevant_parkings = []

 	# Iterate all over the free parking spots
  	for parking in all_parkings:

		if (is_free_parking_time_relevant(parking.last_report_time)):
			lat2 = float(str(parking.parking_address_lat))
			lng2 = float(str(parking.parking_address_lng))
			current_dist = calculate_distance(lat1, lng1, lat2, lng2)
		
		# If the parking time is relevant and the 
		# pariking spot is available and near to dest
			if (current_dist <= radius):
				relevant_parkings.append(parking)

	serialize_relevant_parking = serializers.serialize("json", relevant_parkings)

	return serialize_relevant_parking


def is_free_parking_time_relevant(parking_time): 
	return (minutes_elapsed(parking_time) <= FREE_PARKING_EXISTENCE_TIME)


def get_parkings_by_radius(lat1, lng1, radius, wanted_parking_time):

	all_parkings = Purchase.objects.all()

 	relevant_parkings = []

 	# Iterate all over the offered parking spots
  	for parking in all_parkings:
		parking_time = parking.parking_time
  		
		wanted_parking_time_in_datetime = datetime.datetime.strptime(wanted_parking_time, "%Y-%m-%d %H:%M:%S")
		parking_time_in_datetime = datetime.datetime.strptime(parking_time, "%Y-%m-%d %H:%M:%S")

		diff_in_minutes = (wanted_parking_time_in_datetime - parking_time_in_datetime).total_seconds() / 60


		if (abs(diff_in_minutes) <= THRESHOLD_RELEVANT_PARKING_TIME_DIFF):
			lat2 = float(str(parking.parking_address_lat))
			lng2 = float(str(parking.parking_address_lng))

			current_dist = calculate_distance(lat1, lng1, lat2, lng2)

			if (current_dist <= radius and
				parking.status == ParkingStatus.AVAILABLE):
				relevant_parkings.append(parking)


	serialize_relevant_parking = serializers.serialize("json", relevant_parkings)
	return serialize_relevant_parking


																
# def update_db_free_parking():

# 	all_free_parkings = Purchase.objects.all() # FreeSpot

# 	for parking in all_parkings:
# 		if (is_free_parking_time_relevant(FREE_PARKING_EXISTENCE_TIME)):
# 			parking.delete()

'''
def refresh_map(request):

	current_address 		= request.POST.get("current_address")
	radius 					= int(request.POST.get("radius"))
	relevant_parkings 		= get_parkings_by_radius(current_address, radius, time.now())
	relevant_free_parkings 	= get_free_parkings_by_radius(current_address, radius, time.now())

	update_db_free_parking()

	return render(request, 'polls/show_available_parkings.html', { 	'relevant_parkings' : relevant_parking,\
																	'relevant_free_parkings' : relevant_free_parking })
	
'''

def find_new_parking(request):

	valid_activity = checkIfActivityValid(request)
	if (valid_activity == True):
		request.session["msg"] = "You still have valid activity! End or cancel last activily to create new activity"
		return render(request, 'polls/hotspot.html')
	
	# Asked address
	target_address_lat 	= float(request.POST.get("target_address_lat"))
	target_address_lng 	= float(request.POST.get("target_address_lng"))

	print "target_address_lat: ", target_address_lat
	print "target_address_lng: ", target_address_lng


	# Parking
	parking_id 			= int(request.POST.get("parking_id"))
	print parking_id, "hola"
	chosen_parking 		= Purchase.objects.get(pk=parking_id)

	# Seller
	seller_id 			= int(chosen_parking.seller_id)
	seller_user			= User.objects.get(pk=chosen_parking.seller_id)

	# Buyer
	buyer_user_id 		= int(request.user.pk)
	buyer_user 			= User.objects.get(pk=buyer_user_id)

	if (buyer_user_id == seller_id):
		request.session["msg"] = "Cannot buy your own parking !!!"
		return render(request, 'polls/hotspot.html')

	# The radius according to the zoom of the user's map
	radius 				= request.POST.get("radius")
	

	# Parking location
	parking_address_lat = float(chosen_parking.parking_address_lat)
	parking_address_lng = float(chosen_parking.parking_address_lng)

	# TODO: Remove
	# Lock to edit the object
	# if not chosen_parking.wait_lock(TIMEOUT_AVAILABLE_PARKING):
	# 	chosen_parking.lock.release()
	# 	# TOOD: render to unavailable parking dude or pop-up and render to parking list
	# 	return render(request, 'polls/show_available_parkings.html', 
	# 		{ 'relevant_parkings' : 
	# 			get_parkings_by_radius(asked_target_address, radius, time.now()) })


	# Check buyer has enough points
	if (buyer_user.profile.points < chosen_parking.cost):
		request.session["msg"] = "You do not have enough points!!!"
		return render(request, 'polls/hotspot.html')

	# TODO: Remove
	## Now- locked !

	# If the parking is not free
	if (chosen_parking.status != ParkingStatus.AVAILABLE):
		# TODO: Remove
		#chosen_parking.lock.release()
		
		# TOOD: render to unavailable parking dude or pop-up and render to parking list
		request.session["msg"] = "Parking already booked"
		return render(request, 'polls/hotspot.html')
	

	# In this stage decerase the point only from the buyer 	
	buyer_user.profile.points -= chosen_parking.cost
	buyer_user.save()
	
	# TODO: Last activity for buyer- Notify the buyer the pincode
	pin_code = chosen_parking.pin_code 
	dist_in_meters = calculate_distance(parking_address_lat, parking_address_lng, target_address_lat, target_address_lng)
	parking_rating = dist_to_parking_rate(dist_in_meters)

	# Save data to DB
	update_parking_data(chosen_parking, buyer_user_id, ParkingStatus.IN_PROCESS, parking_rating ,target_address_lat, target_address_lng, pin_code)
	
	# TODO: Remove
	#chosen_parking.lock.release()
	
	# Add purchase to statistics
	now = datetime.datetime.now()
	stat = Statistics( lat = target_address_lat,lng= target_address_lng, hour = int(now.hour),rating =parking_rating, date=chosen_parking.parking_time)

	print("befor = "+str(stat.rating))

	print("statistics created for parking: " + str(parking_id))
	calculate_actual_rating(stat)
	print("after = "+str(stat.rating))


	request.session["msg"] = "Parking booked successfuly. For more details, click on - last activity"
	return render(request, 'polls/hotspot.html')

def dist_to_parking_rate(dist):

	ret = DEFAULT_PARKING_RATE

	if (dist < DIST_HIGH_BOUND_RATE_5):
		ret = 1
	elif (dist < DIST_HIGH_BOUND_RATE_4):
		ret = 0.8
	elif (dist < DIST_HIGH_BOUND_RATE_3):
		ret = 0.6
	elif (dist < DIST_HIGH_BOUND_RATE_2):
		ret = 0.4
	else: 		# ==(dist < DIST_HIGH_BOUND_RATE_1):
		ret = 0.2

	return ret


def update_parking_data(purchase, buyer_id, status,rate,target_address_lat, target_address_lng, pincode):
	purchase.buyer_id			= buyer_id 	# user id
	purchase.status 			= status
   	purchase.parking_rate 		= rate  
	purchase.target_address_lat = target_address_lat
	purchase.target_address_lng = target_address_lng
	purchase.pin_code			= pincode
	purchase.save()


def buyer_cancel_parking(request):
	
	parking_id			= request.POST.get("purchase_id")
	chosen_parking 		= Purchase.objects.get(pk=parking_id)

	seller_id			= int(chosen_parking.seller_id)
	seller				= User.objects.get(pk = seller_id)
	seller.profile.points 	   		+= chosen_parking.cost
	seller.save()

	buyer_user_id  			= int(chosen_parking.buyer_id)
	buyer_user 			= User.objects.get(pk=buyer_user_id)

	buyer_user.profile.rating *= 0.9

	# TODO: Notify seller purchase is cancelled (reason: buyer cancelled) 

	#if chosen_parking.wait_lock(TIMEOUT_LOCK):
	chosen_parking.status = ParkingStatus.AVAILABLE
	chosen_parking.buyer_id = -1
	chosen_parking.target_address = ""
	chosen_parking.parking_rate = 0.0000
	chosen_parking.save()


	data = {'msg': "parking canceled"}
	return JsonResponse(data)


# when seller insert the pincode 
def make_exchange(request):
	parking_id 			= request.POST.get("parking_id")
	offered_parking 	= Purchase.objects.get(pk=parking_id)

	provided_pincode 	= request.POST.get("pincode")
	parking_pincode		= offered_parking.pincode

	seller_user			= User.objects.get(pk=request.user.pk)
	buyer_user 			= User.objects.get(pk=offered_parking.buyer_id)

	if (authenticate_pincode(provided_pincode , parking_pincode)): # if authentication succeeded
		seller.points 			+= chosen_parking.cost
		offered_parking.status   = ParkingStatus.DONE

		# update ratings of the seller and buyer
		update_rating_for_user(seller_user , ParkingStatus.DONE)
		update_rating_for_user(buyer_user , ParkingStatus.DONE)

	else:
		offered_parking.attempt_failure += 1

		if (offered_parking.attempt_failure < THRESHOLD_FAILURES_ATTEMPTS):
			
			# TODO: print authentication failed.. popup screen type again  \ report on buyer
			return render(request, 'polls/wrong_pin_code.html')
		else:
			# TODO: Notify that the deal cancelled - points balance stays unchanged
			buyer_user.points += offered_parking.cost
			buyer_user.save()
			return render(request, 'polls/deal_cancelled.html')
			


#TODO make sure when locking the parking dont need to save the acquiere to the database
#when to save? is the acquiere recursive?
def seller_cancel_parking(request):


	purchase_id			= request.POST.get("purchase_id")
	offered_parking 		= Purchase.objects.get(pk=purchase_id)

	seller_id			= int(offered_parking.seller_id)
	seller_user			= User.objects.get(pk = seller_id)

	buyer_id 			= int(offered_parking.buyer_id)
	if (buyer_id != -1):
		buyer_user 			= User.objects.get(pk=buyer_id)
	
	# Lock to edit the object 
	#if offered_parking.wait_lock(TIMEOUT_LOCK): TODO: what to do with the lock??? 
		


	if (offered_parking.status != ParkingStatus.AVAILABLE): # no harm done



	 	# Someone already bought the parking

		update_parking_data(offered_parking, buyer_id, ParkingStatus.CANCELED,-1,offered_parking.target_address_lat, 								offered_parking.target_address_lng,-1)
		#offered_parking.lock.release()

		seller_user.profile.rating *= 0.9
		#	update_rating_for_user(buyer_user, "Irrelevent")
		
		seller_user.profile.points 	   = (2*offered_parking.cost) 		# Fine seller
		seller_user.profile.points = max(seller_user.profile.points,MIN_POINTS)
		seller_user.profile.save()
		buyer_user.profile.points  += (2*offered_parking.cost) 			# Compensate buyer
		#TODO: notify buyer
		
		buyer_user.save()

	offered_parking.status = ParkingStatus.CANCELED
	offered_parking.save()

	data = {'msg': "parking canceled"}
	return JsonResponse(data)




def authenticate_pincode(provided_pincode, actual_pincode):
	return provided_pincode == actual_pincode

def update_rating_for_user(user, status): #TODO: fix rating for user!!!!!!!!!!!!!!!!!1

	if (status == 'report'):
		user.profile.rating *= FREE_PARKING_RATING_REWARD # Gal
		user.profile.points += FREE_PARKING_POINTS_REWARD

	# Stage 2

	# diff = 0

	# switch() {
	# case ParkingStatus.AVAILABLE:
	# 	diff = 1;
	# }

	# user.rating += diff
	# user.save()
	pass
	
	user.profile.rating = min(user.profile.rating, MAX_RATING)
	user.profile.points = min(user.profile.points, MAX_POINTS)
	user.save()



# Polling 
'''
def provide_streets_to_query(request):

	user_id 				= request.user.pk  		# user id
	user_location 			= request.POST.get("location")
	
	data = request.POST.get('data')

	for street_name, grade in data.iteritems():
		if (grade > 3):

'''

############################################################################################HeatMap
'''
 given a stat_spot - calculate it's relative distance
 for each element in Statstics 
 spot_average = nw1*neighbor_rate_1 + *** +  nwk*neighbor_rate_k
 assume stat_rating was initialized'''
 
#	TODO: init parking_actual_rank  
def calculate_environment_average(spot_stat):
	
	# TODO: Natural neighbor interpolation

	now = datetime.datetime.now()

	neighbors = Statistics.objects.filter(hour =  int(now.hour))
	inverse_dist_list = []
	total_inverst_distance_sum = 0
	normal_value = 0
	weighted_average = 0

	if not neighbors:
		return spot_stat.rating

	# calculate total total_distance_sum and calculate the weight of each neighbor
	for nb in neighbors:

		sLat = float(spot_stat.lat)
		sLng = float(spot_stat.lng)
		nbLat = float(nb.lat)
		nbLng = float(nb.lng)

		# Dist between the spot and the neighbor
		nbDist = calculate_distance(sLat, sLng, nbLat, nbLng)

		# Save the iverse of distance - in order to closesr neighbor will affect more then other
		inverseDist = 0.001 if nbDist == 0 else float(1) / nbDist

		# Sum all inverse for build the normal value later
		total_inverst_distance_sum += inverseDist

		inverse_dist_list.append(inverseDist)

	# Calc the normal value
	normal_value = float(1) / total_inverst_distance_sum
	# calcualte environment_average
	for i in range (0, len(neighbors)):

		# Each neighbor's weight is the inverse of dist (but normalized)
		nbw = float(inverse_dist_list[i]) *  normal_value

		# Sum for calc weighted
		weighted_average += float(neighbors[i].rating) * nbw

	print ("Test gal= " + str(weighted_average))
	return weighted_average


'''
update rank for new statistics object: spot
'''
def calculate_actual_rating(spot_stat):

	spot_rating = float(spot_stat.rating)
	print(calculate_environment_average(spot_stat))
	print(type(calculate_environment_average(spot_stat)))

	stat_rating = ((1-OLD_RANK_WEIGHT) * spot_rating) + (OLD_RANK_WEIGHT * float(calculate_environment_average(spot_stat)))
	spot_stat.rating = stat_rating
	spot_stat.save()



def get_statistics_color_classification():
	#get all statistics from the same hour as now  
	now = datetime.datetime.now()	
	# get all statistics for the current hour from data base
	all_statistics = Statistics.objects.filter(hour =  int(now.hour) )

	print "Before filter", len(list(all_statistics))

	last_week_statistics = filter_statistics_last_week(all_statistics)
	print "After filter", len(last_week_statistics)
	
	stats_to_display = [] 
	
	for stat in last_week_statistics:
		curr_rate = stat.rating
		stat_color = GREEN if curr_rate > COLOR_THRESHOLD else RED # high rating- color in green

		stats_to_display.append({'lat':stat.lat, 'lng':stat.lng, 'color': stat_color})

	return json.dumps(stats_to_display)	# return JsonResponse(spots_to_display)


MINUTES_IN_WEEK = 1 #MINUTES_IN_HOUR*7*24

def filter_statistics_last_week(all_statistics):

	ret = []
	for stat in all_statistics:
		print stat.date
		print minutes_elapsed(stat.date), "gal" 
		if (minutes_elapsed(stat.date) < MINUTES_IN_WEEK): # Minutes in week
			ret.append(stat)

	return ret

# def get_stats_with_colors():
	
# 	statistics_spots = get_statistics_color_classification()
# 	data = {'done_spots': statistics_spots}

# 	return JsonResponse(data)



# def filter_spots_of_last_hours(spots, num_of_hours):

# 	filtered_spots = []
	
# 	for nb in spots:
# 		if (minutes_elapsed(nb.parking_time) <= (MINUTES_IN_HOUR * num_of_hours)):
# 			filtered_spots.append(nb)
# 	return filtered_spots

# def filter_last_days_spots_by_status(num_of_hours, stat):
# 	#get all purchases that were changed to status "done" today 
# 	#TODO: add lambda to the filter, to filter by hour of day 
# 	spots = Purchase.objects.filter(status = stat) # TODO:??? parking_time the parking time is today|| the object was created today )
# 	return filter_spots_of_last_hours(spots, num_of_hours)

	
