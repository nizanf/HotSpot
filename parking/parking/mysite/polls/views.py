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
from .models import Profile, Purchase, FreeSpot
from django.core import serializers
from random import randint
import json
from time import gmtime, strftime
from django.contrib.auth import authenticate, login, logout
from django.http import JsonResponse
from math import radians, cos, sin, asin, sqrt


TIMEOUT_RELOGIN = 10
TIMEOUT_LOCK = 10
TIMEOUT_AVAILABLE_PARKING = 20
THRESHOLD_FAILURES = 5
THRESHOLD_RATING_TO_FREE_SPOT = 5
THRESHOLD_RELEVANT_PARKING_TIME_DIFF = 5
FREE_PARKING_EXISTENCE_TIME = 40
FREE_PARKING_RATING_REWARD = 1.1
FREE_PARKING_POINTS_REWARD = 2
MAX_POINTS = 1000000
MAX_RATING = 5
PINCODE_LEN = 6

def call_login(request):
	return render(request, 'polls/login.html')

def call_homepage(request):
	return render(request, 'polls/hotspot.html')

def call_register(request):
	return render(request, 'polls/register.html')

def call_report(request):
	return render(request, 'polls/report_parking.html')

def call_find(request):
	return render(request, 'polls/find_parking.html')

def call_heatmap(request):
	return render(request, 'polls/heatmap.html')

def call_last_activity(request):

	sell_purchase = Purchase.objects.filter(seller_id = request.user.pk)
	max_pk = 0
	last_activity = None
	buy_purchase = Purchase.objects.filter(buyer_id = request.user.pk)

	for purchase in sell_purchase:
		if (purchase.pk > max_pk):
			max_pk = purchase.pk
			last_activity = purchase


	for purchase in buy_purchase:
		if (purchase.pk > max_pk):
			max_pk = purchase.pk
			last_activity = purchase


	if (last_activity == None):
		last_activity = ["", "", "", "", "", "", "-1"]

		return render(request, 'polls/last_activity', {'last_activity':last_activity }) 


	if (minutes_elapsed(last_activity.parking_time) > 0):
		last_activity.status = "expired"
		last_activity.save()

	seller_username = (User.objects.get(pk = last_activity.seller_id)).username

	if (last_activity.buyer_id == -1):
		buyer_username = "--"
	else:
		buyer_username = (User.objects.get(pk = last_activity.buyer_id)).username

	if (last_activity.seller_id == request.user.pk):
		seller_username = "Me"
		pincode = ""
	else:
		buyer_username = "Me"
		pincode = last_activity.pincode

	last_activity = [buyer_username, seller_username, last_activity.parking_time, last_activity.status, last_activity.parking_address, pincode, last_activity.pk]

	return render(request, 'polls/last_activity.html', {'last_activity':last_activity }) 
	



def aut_pincode(request):

	pincode = request.POST.get("pincode")
	purchase_id = int(request.POST.get("purchase_id"))
	
	purchase = Purchase.objects.get(pk = purchase_id)

	print("our pincode = "+str(pincode)+" type = "+str(type(pincode)))

	print("right pincode = "+str(purchase.pin_code)+" type = "+str(type(purchase.pin_code)))


	if (str(pincode) == purchase.pin_code ):

		purchase.status = "done"

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
	
	free_spot = []	

	for spot in all_free_spot:

		reporters_ids_list = json.loads(reporters_ids_json)
		if request.user.pk in reporters_ids_list:
			free_spot.append(spot)

	all_history = list(sell_purchase) + list(buy_purchase) + list(free_spot)


	all_history.sort(key=lambda x: datetime.datetime.strptime(x.parking_time, "%Y-%m-%d %H:%M:%S") if x.class_name() == "Purchase" else datetime.datetime.strptime(x.last_report_time, "%Y-%m-%d %H:%M:%S"), reverse=True)


	history_as_table = []

	for element in all_history:
		address = element.parking_address

		if element.class_name() == "Purchase":
			elemnt_type = "Purchase"
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
			buyer_username = "--"
			seller_username = "Me"

		current_row = [elemnt_type, address, date_and_time, buyer_username, seller_username]
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


	given_lat = request.POST.get("lat_address")
	given_lng = request.POST.get("lng_address")
	
	request.session["msg"] = ""

	given_parking_address 		= request.POST.get("address") 	

	given_parking_time = strftime("%Y-%m-%d %H:%M:%S", time.localtime())
	given_reporter_id 		= request.user.pk 


	given_street_name = extract_street_name(given_parking_address)

	# Get all parking in the street
	parking_in_street = FreeSpot.objects.filter(street_name=given_street_name)


	found_valid_parking = False

	if parking_in_street:

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
				if parking.is_verified:
					# Update rank/points to given_reporter_id user
					reporter_user = User.objects.get(pk=given_reporter_id)
					update_rating_for_user(reporter_user,'report')
						

				# If the parking rank is over the threshold - add points to 
				# the reporters and show it in the map
				else: 
					if (parking.parking_rank >= THRESHOLD_RATING_TO_FREE_SPOT):
						parking.is_verified = 1
						for usr_id in free_parking:
							# Update rank/points to given_reporter_id user
							reporter_user = User.objects.get(pk=user_id)
							update_rating_for_user(reporter_user,'report')
							

				parking.save()
				break


	# If we did not find the parking - add to the list
	if not found_valid_parking:
		free_parking = FreeSpot(reporters_ids = json.dumps([given_reporter_id]), last_report_time = given_parking_time, 						parking_address = given_parking_address, street_name = given_street_name, 							parking_address_lat = given_lat, parking_address_lng = given_lng, 
						parking_rank = request.user.profile.rating)
		free_parking.save()



	return render(request, 'polls/hotspot.html')


def clear_msg(request):
   	if request.is_ajax() and request.method=='POST':
   		print(request.session['msg'])

        request.session['msg'] = "" 
        print(request.session['msg'])
        return HttpResponse("cleared message")


def update_user_spots_status(given_seller_id):
	sell_spot_list = Purchase.objects.filter(seller_id = given_seller_id, status = "available")
	for spot in sell_spot_list:
		if (spot.status == "available" or spot.status == "in process"):
			print("\n\n\n "+str(minutes_elapsed(spot.parking_time))+" \n\n\n")
			if (minutes_elapsed(spot.parking_time) > 0):
				
				spot.status = "expired"
				print("expired")
				spot.save()




def offer_new_parking(request):

	given_lat = request.POST.get("lat_address")
	given_lng = request.POST.get("lng_address")
	
	request.session["msg"] = ""

	given_seller_id 		= int(request.user.pk)  

	update_user_spots_status(given_seller_id)

	if (Purchase.objects.filter(seller_id = given_seller_id, status = "available") or Purchase.objects.filter(seller_id = given_seller_id, status = "in process")):
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
    lon1, lat1, lon2, lat2 = map(radians, [lon1, lat1, lon2, lat2])
    # haversine formula 
    dlon = lon2 - lon1 
    dlat = lat2 - lat1 
    a = sin(dlat/2)**2 + cos(lat1) * cos(lat2) * sin(dlon/2)**2
    c = 2 * asin(sqrt(a)) 
    # Radius of earth in kilometers is 6371
    m = 6371* c*1000
    return m


def update_spots_on_map(request):
	print("here")


	lat = float(request.POST.get('lat'))
	if (not lat): 
		lat = float(32.121678)

	lng = float(request.POST.get('lng'))
	if (not lng):
		lat = float(34.791143)

	radius = float(request.POST.get('radius'))
	if (not radius): 
		radius = 100
	print ('1')
	given_parking_time_in_minutes = int(request.POST.get('minutes'))
	print ('2')
	now = datetime.datetime.now()
	time_delta = now + datetime.timedelta(minutes = given_parking_time_in_minutes)
	print ('3')
	given_parking_time = strftime("%Y-%m-%d %H:%M:%S", time_delta.timetuple())


	
	relevant_parkings 	= get_parkings_by_radius(lat, lng, radius, given_parking_time)
	relevant_free_parkings 	= get_free_parkings_by_radius(lat, lng, radius, given_parking_time)



	data = {'relevant_parkings': relevant_parkings, 'relevant_free_parkings': relevant_free_parkings}


	return JsonResponse(data)




def get_free_parkings_by_radius(lat1, lng1, radius, parking_time):
	
	all_parkings = FreeSpot.objects.all()
 	relevant_parkings = []

 	# Iterate all over the free parking spots
  	for parking in all_parkings:

		if (is_free_parking_time_relevant(parking.last_report_time)):
			lat2 = parking.parking_address_lat
			lng2 = parking.parking_address_lng
			current_dist = calculate_distance(lat1, lng1, lat2, lng2)
		
		# If the parking time is relevant and the 
		# pariking spot is available and near to dest
			if (current_dist <= radius):
				relevat_parkings.append(parking)

	serialize_relevant_parking = serializers.serialize("json", relevant_parkings)

	return serialize_relevant_parking


def is_free_parking_time_relevant(parking_time): 
	return (minutes_elapsed(parking_time) <= FREE_PARKING_EXISTENCE_TIME)


def get_parkings_by_radius(lat1, lng2, radius, wanted_parking_time):
	
	all_parkings = Purchase.objects.all()

 	relevant_parkings = []

 	# Iterate all over the offered parking spots
  	for parking in all_parkings:
		parking_time = parking.parking_time
		wanted_parking_time_in_datetime = datetime.datetime.strptime(wanted_parking_time, "%Y-%m-%d %H:%M:%S")
		parking_time_in_datetime = datetime.datetime.strptime(parking_time, "%Y-%m-%d %H:%M:%S")

		diff_in_minutes = (wanted_parking_time_in_datetime - parking_time_in_datetime).total_seconds() / 60


		if (abs(diff_in_minutes) <= THRESHOLD_RELEVANT_PARKING_TIME_DIFF):

			lat2 = parking.parking_address_lat
		 	lng2 = parking.parking_address_lng

			current_dist = calculate_distance(lat1, lng1, lat2, lng2)
		
			if (current_dist <= radius and
				parking.status == "available"):
				relevat_parkings.append(parking)

	serialize_relevant_parking = serializers.serialize("json", relevant_parkings)
	return serialize_relevant_parking


																
def update_db_free_parking():

	all_free_parkings = Purchase.objects.all()

	for parking in all_parkings:
		if (is_free_parking_time_relevant(FREE_PARKING_EXISTENCE_TIME)):
			parking.delete()

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
'''
def find_new_parking(request):
	
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
		return render(request, 'polls/show_available_parkings.html', 
			{ 'relevant_parkings' : 
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

'''

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

	return render(request, 'polls/hotspot.html')


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
			return render(request, 'polls/hotspot.html')

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

	return render(request, 'polls/hotspot.html')


def generate_new_pin_code():
	return randint(1000, 9999)
		
	
def authenticate_pincode(provided_pincode, actual_pincode):
	return provided_pincode == actual_pincode


def update_rating_for_user(user, status):

	if (status == 'report'):
		user.rank *= FREE_PARKING_RATING_REWARD # Gal
		user.points += FREE_PARKING_POINTS_REWARD

	# Stage 2

	# diff = 0

	# switch() {
	# case "available":
	# 	diff = 1;
	# }

	# user.rating += diff
	# user.save()
	pass
	
	user.rank = min(user.rank, MAX_RATING)
	user.points = min(user.points, MAX_POINTS)
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




