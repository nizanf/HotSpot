# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.shortcuts import render
from django.http import HttpResponse
from django.shortcuts import render

from django.contrib.auth import authenticate
from django.contrib.auth import logout

from django.contrib.auth.models import User
from .models import Profile, Purchase

from django.core import serializers

import datetime
# for lock 
import threading
import time
from random import randint



TIMEOUT_AVAILABLE_PARKING = 20

def login(request):
	given_username = request.POST.get("username") #in template, div name = username.
	given_password = request.POST.get("password") #in template, div name = password.

	auth_code = authenticate(username=given_username, password=given_password)

	if auth_code : #login succeed
		return render(request, 'polls/homepage.html')
	else: # login failed
       	return render(request, 'polls/relogin.html')


def register(request):
	given_username 		= request.POST.get("username") 		# in template, div name = username.
	given_first_name 	= request.POST.get("first_name") 	# in template, div name = first_name.
	given_last_name 	= request.POST.get("last_name") 	# in template, div name = last_name.
	given_email 		= request.POST.get("email") 		# in template, div name = email.
	given_password	 	= request.POST.get("password") 		# in template, div name = password.
	given_phone_number 	= request.POST.get("phone_number") 	# in template, div name = phone_number.

	new_user = User.objects.create_user(username=given_username, \
	 		password = given_password, email = given_email, \
	 		first_name = given_first_name, last_name = given_last_name)

	new_user.profile.phone_number = given_phone_number
	new_user.save()

	# TODO : Add message: register successfully
	return render(request, 'polls/login.html')

# OR - Danny and gal wants to remove
#	new_user = authenticate(username=given_username, password=given_password)
#	return render(request, 'polls/homepage.html')

def logout(request):
	logout(request)
	return render(request, 'polls/login.html')

def offer_new_parking(request):
	
	given_seller_id 		= request.user  					# user id
	given_parking_address 	= request.POST.get("location") 	# TODO: verify the nitzans give us the location
	given_parking_time 		= request.POST.get("parking_time")
	purchase 				= Purchase(	purchase_id =getPurchaseID(), seller_id = given_seller_id,\
									 	parking_address = given_parking_address, \
									 	parking_time = given_parking_time)


	# TODO: Add event log

	purchase.save()

	# seller_user			 	= User.objects.get(pk=given_seller_id)
	# seller_user.numOfPurchases =+1 
	# seller_user.save()

	return render(request, 'polls/homepage.html')


def search_parking(request):
	given_target_address 	= request.POST.get("target_location") 	# TODO: verify nitzan give us the location
	radius 					= int(request.POST.get("radius")) 	
	parking_time 			= request.POST.get("parking_time") 	# TODO: verify nitzan give us the location
	relevant_parkings 		= get_parkings_by_radius(given_target_address, radius, parking_time)

	return render(request, 'polls/show_available_parkings.html', { 'relevant_parkings' : relevant_parkings })



def get_parkings_by_radius(target_address, radius, parking_time):
	
	# TODO: Not sure this is all the prakings, why Purchase?
	all_parkings = Purchase.objects.all()

 	relevat_parkings = []

  	for parking in all_parkings:
		current_dist = calculate_distance(parking.parking_address,target_address)
		if (parking_time <= parking.pub_date and \
			current_dist <= radius and
			parking.status == "available"):
			relevat_parkings.append(parking)

	serialize_relevant_parking = serializers.serialize("json", relevant_parkings)
	return serialize_relevant_parking


def calculate_distance(address1, address2):
	return 0 # TODO: Implement function


def refresh_map(request):

	current_address 	= request.POST.get("current_address")
	radius 				= int(request.POST.get("radius"))
	relevant_parkings 	= get_parkings_by_radius(current_address, radius, time.now())

	return render(request, 'polls/show_available_parkings.html', { 'relevant_parkings' : relevant_parking })




def catch_parking(request):
	asked_target_address = request.POST.get("asked_target_address")
	seller_user	= User.objects.get(pk=chosen_parking.seller_id)

	buyer_user_id 		 = request.user
	buyer_user 	= User.objects.get(pk=buyer_user_id)

	# The radius according to the zoom of the user's map
	radius 				= request.POST.get("radius")
	parking_id 			= request.POST.get("parking_id")
	chosen_parking 		= Purchase.objects.get(pk=parking_id)

	# Check buyer has enough points
	if (buyer_user.score < chosen_parking.cost):
		# TODO: Render to - sorry dude page - No enough points
		# In the page link to report points
		return render(request, 'polls/no_points_page.html')

	# If the parking is not free
	if (chosen_parking.status != "available"):
		# TOOD: render to unavailable parking dude or pop-up and render to parking list
		return render(request, 'polls/show_available_parkings.html', \
			{ 'relevant_parkings' : \
				get_parkings_by_radius(asked_target_address, radius, time.now()) })
	

	# Lock to edit the object
	if not chosen_parking.wait_lock(TIMEOUT_AVAILABLE_PARKING):

		# TOOD: render to unavailable parking dude or pop-up and render to parking list
		return render(request, 'polls/show_available_parkings.html', \
			{ 'relevant_parkings' : \
				get_parkings_by_radius(asked_target_address, radius, time.now()) })


	chosen_parking.status = "in process"
	chosen_parking.lock.release()
	
	pin_code = generate_new_pin_code() # TODO: Show the buyer the pincode

	rate = calculate_distance(given_target_address, chosen_parking.parking_address)
	reset_parking(chosen_parking, buyer_user_id, "in process",rate,asked_target_address,pin_code)

	# chosen_parking.pin_code 		= pincode
	# chosen_parking.status 			= "in process"
	# chosen_parking.buyer_id 		= buyer_user_id	# get user id
	# chosen_parking.parking_rate 	= calculate_distance(given_target_address, chosen_parking.parking_address)
	# chosen_parking.target_address 	= asked_target_address
	# chosen_parking.save()
		
	# In this stage decerase the point only from the buyer 	
	buyer_user.points -= chosen_parking.cost
	buyer_user.save()

	return render(request, 'polls/parking_purchased.html')


def buyer_cancel_parking(request):
	
	buyer_user_id 		= request.user
	parking_id 			= request.POST.get("parking_id")
	chosen_parking 		= Purchase.objects.get(pk=parking_id)
	
	seller_id 			= chosen_parking.seller_id
	seller_user			= User.objects.get(pk=seller_id)

	seller.points 	   += chosen_parking.cost

	buyer_user 			=  User.objects.get(pk=buyer_user_id)
	update_rating_for_user(buyer_user , "cancel")

	#TODO: add lock because the seller may try to cancel
	chosen_parking.status = "available"
	chosen_parking.buyer_id = -1
	chosen_parking.parking_address = models.CharField(max_length=200)
	chosen_parking.parking_rate = -1

	seller.save()
	chosen_parking.save()

	return render(request, 'polls/homepage.html')


# when seller insert the pincode 
def make_exchange(request):
	parking_id 			= request.POST.get("parking_id")
	offered_parking 	= Purchase.objects.get(pk=parking_id)

	provided_pincode 	= request.POST.get("pincode")
	parking_pincode		= offered_parking.pincode

	seller_user			= User.objects.get(pk=request.user)
	buyer_user 			= User.objects.get(pk=offered_parking.buyer_id)

	if (authenticate_pincode(provided_pincode , parking_pincode)) # if authentication succeeded
		seller.points 			+= chosen_parking.cost
		offered_parking.status   = 'done'

		# update ratings of the seller and buyer
		update_rating_for_user(seller_user , "done")
		update_rating_for_user(buyer_user , "done")

	else
		# TODO: print authentication failed.. popup screen type again  \ report on buyer


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


	seller_user			= User.objects.get(pk=request.user)
	offered_parking_id 	= request.POST.get("parking_id")
	offered_parking 	= Purchase.objects.get(pk=parking_id)
	buyer_id 			= offered_parking.buyer_id
	buyer_user 			= User.objects.get(pk=offered_parking.buyer_id)
	
	# Lock to edit the object
	if offered_parking.wait_lock(TIMEOUT_AVAILABLE_PARKING):
		if (offered_parking.status == "available"): # no harm done
			reset_parking(offered_parking, -1, "Irrelevent",-1, None, -1)
			offered_parking.lock.release()
			return render(request, 'polls/homepage.html')

		else : #someone already bought the parking
			reset_parking(offered_parking, buyer_id, "canceled",-1,offered_parking.target_address,-1)
			offered_parking.lock.release()
			update_rating_for_user(seller, "canceled")
			update_rating_for_user(buyer_user, "Irrelevent")
			seller.points 	   -= (2*chosen_parking.cost) 			#fine seller
			seller.save()
			buyer_user.points  += (2*chosen_parking.cost) 			#compensate buyer
			#TODO: notificate buyer
			buyer_user.save()

	return render(request, 'polls/homepage.html')

def generate_new_pin_code():
	return randint(1000, 9999)
		
	
def authenticate_pincode(provided_pincode, actual_pincode):
	return provided_pincode == actual_pincode


def update_rating_for_user(user, status):


	# diff = 0

	# switch() {
	# case "available":
	# 	diff = 1;
	# }

	# user.rating += diff
	# user.save()
	pass

