# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models
from django.contrib.auth.models import User
from django.db.models.signals import post_save
from django.dispatch import receiver
from decimal import Decimal



# for lock 
import threading
import time
import datetime

class Profile(models.Model):
	user = models.OneToOneField(User, on_delete=models.CASCADE)
	
	phone_number 	= models.CharField(max_length=20, blank=True)
	points 		= models.IntegerField(default=50) #start with 50 points.
	rating 		= models.IntegerField(default=2) # start with rating 2
	is_blocked 	= models.IntegerField(default=0) # start with is blocked 0.
	num_reported 	= models.IntegerField(default=0) # start with 0 reported purchases


# TODO: Add doc
@receiver(post_save, sender=User)
def create_user_profile(sender, instance, created, **kwargs):
	if created:
		Profile.objects.create(user=instance)

# TODO: Add doc
@receiver(post_save, sender=User)
def save_user_profile(sender, instance, **kwargs):
  	instance.profile.save()


class Purchase(models.Model):
	buyer_id	= models.IntegerField(default=-1) 	# user id
	seller_id	= models.IntegerField(default=-1) 	# user id
	cost 		= models.IntegerField(default=10)
	parking_time 	= models.CharField(max_length=200, default="") #  max 30 minutes from the offering time
	status 		= models.CharField(max_length=200, default="available") # available, in process, done, canceled, expired etc.
	parking_rate 	= models.DecimalField(max_digits=3,decimal_places=2,default=Decimal('0.0000'))
	
	target_address_lat = models.CharField(max_length=2000)
	target_address_lng = models.CharField(max_length=2000)
	
	parking_address = models.CharField(max_length=200) #string. full address
	parking_address_lat = models.CharField(max_length=2000)
	parking_address_lng = models.CharField(max_length=2000)

	lock 			= threading.Lock()
	cond 			= threading.Condition(threading.Lock())
	pin_code		= models.CharField(max_length=2000, default="-1")
	attempt_failure = models.IntegerField(default=0)

	parking_actual_rank = models.DecimalField(max_digits=3,decimal_places=2,default=Decimal('0.0000'))


	def class_name(self):
    		return Purchase.__name__


class FreeSpot(models.Model):
	reporters_ids	= models.CharField(default="", max_length = 20000) 	# user id
	last_report_time= models.CharField(max_length=200, default="") #  max 30 minutes from the offering time

	parking_address = models.CharField(max_length=200) #coordinates of parking address. (x,y)

	street_name		= models.CharField(max_length=200) # Parking street name
	parking_address_lat = models.CharField(max_length=2000)
	parking_address_lng = models.CharField(max_length=2000)

	lock 			= threading.Lock()
	cond 			= threading.Condition(threading.Lock())
	parking_rank	= models.IntegerField(default=0) # start with rating 0
	is_verified		= models.IntegerField(default=0) # start with rating 0

	def class_name(self):
    		return FreeSpot.__name__


class Statistics(models.Model):
	
	lat = models.CharField(max_length=2000)
	lng = models.CharField(max_length=2000)

	hour 				= models.IntegerField(default=0)
	rating				= models.DecimalField(max_digits=8,decimal_places=7,default=Decimal('0.0000'))
	date				= models.CharField(max_length=200, default="") #  max 30 minutes from the offering time
	
