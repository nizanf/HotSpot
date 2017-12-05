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

def login(request):
	given_username = request.POST.get("username") #in template, div name = username.
	given_password = request.POST.get("password") #in template, div name = password.

	user = authenticate(username=given_username, password=given_password)

	if user : #login succeed
		return render(request, 'polls/homepage.html')
	else: # login failed
       		return render(request, 'polls/relogin.html')

def register(request):
	given_username = request.POST.get("username") #in template, div name = username.
	given_first_name = request.POST.get("first_name") #in template, div name = first_name.
	given_last_name = request.POST.get("last_name") #in template, div name = last_name.
	given_email = request.POST.get("email") #in template, div name = email.
	given_password = request.POST.get("password") #in template, div name = password.
	given_phone_number = request.POST.get("phone_number") #in template, div name = phone_number.

	user = User.objects.create_user(username=given_username, password = given_password, email = given_email, first_name = given_first_name, last_name = given_last_name)

	user.profile.phone_number = given_phone_number
	user.save()

	user = authenticate(username=given_username, password=given_password)

	return render(request, 'polls/homepage.html')

def logout(request):
	logout(request)
	return render(request, 'polls/login.html')

def offer_new_parking(request):
	given_sell = request.user  					# user id
	given_parking_address =  request.POST.get("location") 	# TODO: verify the nitzans give us the location
	given_parking_time = request.POST.get("parking_time")
	purchase = Purchase(sell = given_sell, parking_address = given_parking_address, parking_time = given_parking_time)

	# TODO: Add event log
	# TODO: Add debug log

	purchase.save()

	return render(request, 'polls/homepage.html')


def search_parking(request):
	given_target_address =  request.POST.get("target_location") 	# TODO: verify the nitzans give us the location
	radius =  int(request.POST.get("radius")) 	
	parking_time =  request.POST.get("parking_time") 	# TODO: verify the nitzans give us the location
	relevant_parkings = get_parkings_by_radius(given_target_address, radius, parking_time)

	serialize_relevant_parking = serializers.serialize("json", relevant_parkings)

	return render(request, 'polls/show_available_parkings.html', {'relevant_parkings':relevant_parkings})



def get_parkings_by_radius(target_address, radius, parking_time):
	all_parkings = Purchase.objects.all()
 	relevat_parkings = []

  	for parking in all_parkings:
		current_dist = calculate_distance(parking.parking_address,target_address)
		if (current_dist<radius and parking_time<parking.pub_date):
			relevat_parkings.append(parking)

	return relevat_parkings


def calculate_distance(address1, address2):
	return 0 # TO-DO: edit function


def catch_parking(request):
	given_target_address = request.POST.get("target_address")
	parking_id = request.POST.get("parking_id")
	chosen_parking = Purchase.objects.get(pk=parking_id)

	while (chosen_parking.locked):# TO-DO: add lock properly
		pass
	chosen_parking.lock()

	buy_user = User.objects.get(pk=chosen_parking.buy)
	sell_user = User.objects.get(pk=chosen_parking.sell)

	if (buy_user.score < chosen_parking.cost)
		# TODO: Render to - sorry dude page - No enough points
		# In the page link to report points
		return render(request, 'polls/no_points_page.html')

	

	if (chosen_parking.status == "pending"):
		chosen_parking.status = "in process"
		chosen_parking.buy = request.user # get user id
		chosen_parking.parking_rate = calculate_distance(given_target_address, chosen_parking.parking_address)
		chosen_parking.target_address = given_target_address
		chosen_parking.save()
			
		buy_user.score -= chosen_parking.cost
		buy_user.save()
	else: # Status not pending
		# TODO: Notification of - Sorry dude - parking not availability
		# TODO: Render to search page
		
	









 






