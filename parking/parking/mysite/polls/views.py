# -*- coding: utf-8 -*-
from __future__ import unicode_literals

import datetime
# for lock 
import threading
import time

from django.shortcuts import render
from django.http import HttpResponse
from django.template import loader
from django.contrib.auth import authenticate
from django.contrib.auth import logout
from django.contrib.auth.models import User
from .models import Profile, Purchase
from django.core import serializers
from random import randint
import json
from time import gmtime, strftime



TIMEOUT_RELOGIN = 10
TIMEOUT_LOCK = 10
TIMEOUT_AVAILABLE_PARKING = 20
THRESHOLD_FAILURES = 5
THRESHOLD_RATING_TO_FREE_SPOT = 5
FREE_PARKING_EXISTENCE_TIME = 30


def call_login(request):
	return render(request, 'polls/login.html')

def call_homepage(request):
	return render(request, 'polls/HotSpot.html')

def call_register(request):
	return render(request, 'polls/register.html')

def call_report(request):
	return render(request, 'polls/find_parking.html')

def call_heatmap(request):
	return render(request, 'polls/heatmap.html')

def call_history(request):
	return render(request, 'polls/history.html')

def call_offer(request):
	return render(request, 'polls/offer_parking.html')


def login_user(request):
	request.session["msg"] = ""

	"""
		Login method
	"""
	if ('login_failures' in request.session and 
		request.session['login_failures'] >= THRESHOLD_FAILURES and 
		diff_minutes(request.session['last_failure']) < TIMEOUT_RELOGIN ):

			request.session['msg'] = str("The user is locked for {0} minutes".format(TIMEOUT_RELOGIN))

			print("request.session['login_failures'] = "+str(request.session['login_failures']))			
			print("diff_minutes(request.session['last_failure']) = "+str(diff_minutes(request.session['last_failure'])))
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
	  	request.session['login_failures'] = 0
	  	request.session['last_failure'] = None
		return render(request, 'polls/is_login.html', {"is_login":"true"})
	

	else: # login failed	
		print("failed")
		request.session['login_failures'] = request.session['login_failures'] + 1 if 'login_failures' in request.session else 1
		request.session['last_failure'] = strftime("%Y-%m-%d %H:%M:%S", gmtime())

	  	request.session["msg"] = "username or password incorrect!"
	  	return render(request, 'polls/is_login.html', {"is_login":"false"})


def diff_minutes(last_failure_in_string):
	"""
		Return True if user is still in timeout
	"""
	print("in diff_minutes")
	last_failure_in_datetime = datetime.datetime.strptime(last_failure_in_string, "%Y-%m-%d %H:%M:%S")

	diff = (datetime.datetime.now() - last_failure_in_datetime)
	print("diff = "+str(diff.total_seconds() / 60))
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
	"""	
		Logout method
	"""
	logout(request)
	return render(request, 'polls/login.html')


def report_free_parking(request):

	given_reporter_id 		= request.user.pk  		# user id
	given_parking_address 	= request.POST.get("location")
	given_parking_time 		= request.POST.get("parking_time")
	given_parking_street	= request.POST.get("parking_street")

	# Get all parking in the street
	parking_in_street = FreeParking.objects.get(street_name=given_parking_street)

	found_valid_parking = False

	if parking_in_street:

		for parking in parking_in_street:
			
			diff_time = diff_minutes(parking.parking_time)

			# If the parking is still relvent
			if diff_time < FREE_PARKING_EXISTENCE_TIME:

				found_valid_parking = True

				reporters_ids_json = parking.reporters_ids
				reporters_ids_list = json.loads(reporters_ids_json)
				reporters_ids_list.append(given_reporter_id)
				reporters_ids_json = json.dumps(reporters_ids_list)
				parking.reporters_ids = reporters_ids_json
				parking.parking_rank += request.user.profile.rating

				# If there is enough rating of reporters to verify
				# the parking
				if parking.is_verified:
					# TODO: add rank/points to given_reporter_id user
					pass

				# If the parking rank is over the threshold - add points to 
				# the reporters and show it in the map
				else: 
					if (parking.parking_rank >= THRESHOLD_RATING_TO_FREE_SPOT):
						parking.is_verified = 1
						for usr_id in free_parking:
							#TODO: add rank/points
							pass


				parking.save()
				break


	# If we did not find the parking - add to the list
	if not found_valid_parking:
		free_parking = FreeSpot(reporters_ids = json.dumps([given_reporter_id]), parking_time = given_parking_time, parking_address = parking_in_street, street_name = parking_in_street, parking_rank = request.user.profile.rating)
		free_parking.save()

	# TODO: Add event log

	return render(request, 'polls/homepage.html')


def offer_new_parking(request):
	
	given_seller_id 		= request.user.pk  						# User id
	given_parking_address 	= request.POST.get("location") 			
	given_parking_time 		= request.POST.get("parking_time")
	
	purchase 				= Purchase(	purchase_id =getPurchaseID(), seller_id = given_seller_id,\
									 	parking_address = given_parking_address, \
									 	parking_time = given_parking_time)


	# TODO: Add event log

	purchase.save()

	return render(request, 'polls/homepage.html')


def search_parking(request):
	given_target_address 	= request.POST.get("target_location") 	# TODO: Verify nizan give us the location
	radius 					= int(request.POST.get("radius")) 		
	parking_time 			= request.POST.get("parking_time") 		# TODO: Verify nitzan give us the location

	relevant_parkings 		= get_parkings_by_radius(given_target_address, radius, parking_time)
	relevant_free_parkings 	= get_free_parkings_by_radius(given_target_address, radius, parking_time)
	
	return render(request, 'polls/show_available_parkings.html', { 'relevant_parkings' : relevant_parkings, \
																	'relevant_free_parkings' : relevant_free_parkings })


def get_free_parkings_by_radius(target_address, radius, parking_time):
	
	# TODO: Not sure this is all the prakings, why Purchase?
	all_parkings = FreeSpot.objects.all()
 	relevat_parkings = []

 	# Iterate all over the free parking spots
  	for parking in all_parkings:

		current_dist = calculate_distance(parking.parking_address,target_address)
		
		# If the parking time is relevant and the 
		# pariking spot is available and near to dest
		if (is_free_parking_time_relevant(parking.last_report_time) and \
			current_dist <= radius):
			relevat_parkings.append(parking)

	serialize_relevant_parking = serializers.serialize("json", relevant_parkings)

	return serialize_relevant_parking


def is_free_parking_time_relevant(parking_time): 
	return (diff_minutes(parking_time) <= FREE_PARKING_EXISTENCE_TIME)


def get_parkings_by_radius(target_address, radius, parking_time):
	
	all_parkings = Purchase.objects.all()

 	relevat_parkings = []

 	# Iterate all over the offered parking spots
  	for parking in all_parkings:

		current_dist = calculate_distance(parking.parking_address,target_address)
		
		if (parking_time <= parking.parking_time and \
			current_dist <= radius and
			parking.status == "available"):
			relevat_parkings.append(parking)

	serialize_relevant_parking = serializers.serialize("json", relevant_parkings)
	return serialize_relevant_parking


def calculate_distance(address1, address2):
	# TODO: Implement function
	return 0

																
def update_db_free_parking():

	all_free_parkings = Purchase.objects.all()

	for parking in all_parkings:
		if (is_free_parking_time_relevant(FREE_PARKING_EXISTENCE_TIME)):
			parking.delete()


def refresh_map(request):

	current_address 		= request.POST.get("current_address")
	radius 					= int(request.POST.get("radius"))
	relevant_parkings 		= get_parkings_by_radius(current_address, radius, time.now())
	relevant_free_parkings 	= get_free_parkings_by_radius(current_address, radius, time.now())

	update_db_free_parking()

	return render(request, 'polls/show_available_parkings.html', { 	'relevant_parkings' : relevant_parking,\
																	'relevant_free_parkings' : relevant_free_parking })
	

def catch_parking(request):
	
	asked_target_address 	= request.POST.get("asked_target_address")
	seller_user				= User.objects.get(pk=chosen_parking.seller_id)

	buyer_user_id 		 	= request.user.pk
	buyer_user 				= User.objects.get(pk=buyer_user_id)

	# The radius according to the zoom of the user's map
	radius 				= request.POST.get("radius")
	parking_id 			= request.POST.get("parking_id")
	chosen_parking 		= Purchase.objects.get(pk=parking_id)


	# Lock to edit the object
	if not chosen_parking.wait_lock(TIMEOUT_AVAILABLE_PARKING):
		chosen_parking.lock.release()
		# TOOD: render to unavailable parking dude or pop-up and render to parking list
		return render(request, 'polls/show_available_parkings.html', \
			{ 'relevant_parkings' : \
				get_parkings_by_radius(asked_target_address, radius, time.now()) })


	# Check buyer has enough points
	if (buyer_user.score < chosen_parking.cost):
		
		# In the page link to report points
		return render(request, 'polls/no_points_page.html')


	## Now- locked !

	# If the parking is not free
	if (chosen_parking.status != "available"):
		chosen_parking.lock.release()
		# TOOD: render to unavailable parking dude or pop-up and render to parking list
		return render(request, 'polls/show_available_parkings.html', \
			{ 'relevant_parkings' : \
				get_parkings_by_radius(asked_target_address, radius, time.now()) })
	
	# In this stage decerase the point only from the buyer 	
	buyer_user.points -= chosen_parking.cost
	buyer_user.save()
	
	# TODO: Notify the buyer the pincode
	pin_code = generate_new_pin_code() 

	rate = calculate_distance(given_target_address, chosen_parking.parking_address)
	reset_parking(chosen_parking, buyer_user_id, "in process",rate,asked_target_address,pin_code)
	
	chosen_parking.lock.release()
	
	return render(request, 'polls/parking_purchased.html')


def buyer_cancel_parking(request):
	
	buyer_user_id 		= request.user.pk
	parking_id 			= request.POST.get("parking_id")
	chosen_parking 		= Purchase.objects.get(pk=parking_id)
	
	seller_id 			= chosen_parking.seller_id
	seller_user			= User.objects.get(pk=seller_id)

	seller.points 	   += chosen_parking.cost
	seller.save()
	
	buyer_user 			=  User.objects.get(pk=buyer_user_id)
	
	update_rating_for_user(buyer_user , "cancel")

	# TODO: Notify seller purchase is cancelled (reason: buyer cancelled) 

	if chosen_parking.wait_lock(TIMEOUT_LOCK):
		chosen_parking.status = "available"
		chosen_parking.buyer_id = -1
		chosen_parking.target_address = models.CharField(max_length=200)
		chosen_parking.parking_rate = -1
		chosen_parking.save()

	return render(request, 'polls/homepage.html')


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
		offered_parking.status   = 'done'

		# update ratings of the seller and buyer
		update_rating_for_user(seller_user , "done")
		update_rating_for_user(buyer_user , "done")

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
			

def reset_parking(purchase, buyer_id, status,rate,target_address,pincode):
	purchase.buyer_id			= buyer_id 	# user id
	purchase.status 			= status
   	purchase.parking_rate 		= rate  
	purchase.target_address 	= target_address
	purchase.pin_code			= pincode
	offered_parking.save()

#TODO make sure when locking the parking dont need to save the acquiere to the database
#when to save? is the acquiere recursive?
def seller_cancel_parking(request):


	seller_user			= User.objects.get(pk=request.user.pk)
	
	offered_parking_id 	= request.POST.get("parking_id")
	offered_parking 	= Purchase.objects.get(pk=offered_parking_id)

	buyer_id 			= offered_parking.buyer_id
	buyer_user 			= User.objects.get(pk=buyer_id)
	
	# Lock to edit the object 
	if offered_parking.wait_lock(TIMEOUT_LOCK):
		
		if (offered_parking.status == "available"): # no harm done
			offered_parking.delete()
			offered_parking.lock.release()
			return render(request, 'polls/homepage.html')

		else : # Someone already bought the parking
			reset_parking(offered_parking, buyer_id, "canceled",-1,offered_parking.target_address,-1)
			offered_parking.lock.release()

			update_rating_for_user(seller, "canceled")
			update_rating_for_user(buyer_user, "Irrelevent")
			
			seller.points 	   -= (2*chosen_parking.cost) 			# Fine seller
			seller.save()
			buyer_user.points  += (2*chosen_parking.cost) 			# Compensate buyer
			#TODO: notify buyer
			buyer_user.save()

	return render(request, 'polls/homepage.html')


def generate_new_pin_code():
	return randint(1000, 9999)
		
	
def authenticate_pincode(provided_pincode, actual_pincode):
	return provided_pincode == actual_pincode


def update_rating_for_user(user, status):

	# Stage 2

	# diff = 0

	# switch() {
	# case "available":
	# 	diff = 1;
	# }

	# user.rating += diff
	# user.save()
	pass


# Polling 
'''
def provide_streets_to_query(request):

	user_id 				= request.user.pk  		# user id
	user_location 			= request.POST.get("location")
	
	data = request.POST.get('data')

	for street_name, grade in data.iteritems():
		if (grade > 3):

'''




