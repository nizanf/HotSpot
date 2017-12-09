# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models
from django.contrib.auth.models import User
from django.db.models.signals import post_save
from django.dispatch import receiver

# for lock 
import threading
import time

class Profile(models.Model):
	user = models.OneToOneField(User, on_delete=models.CASCADE)
	
	phone_number = models.CharField(max_length=20, blank=True)
    points 	= models.IntegerField(default=50) #start with 50 points.
    rating 	= models.IntegerField(default=0) # start with rating 0.

  #   numOfPurchases = models.IntegerField(default=0) # start 0 purcahses
 	# numOfSuccessfull = models.IntegerField(default=0)
 	# numOfIrrelevent 	 = models.IntegerField(default=0)
 	# numOfCanceled 	 = models.IntegerField(default=0)

	

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
#	purchase_id		= models.IntegerField(default=-1)
	buyer_id		= models.IntegerField(default=-1) 	# user id
	seller_id		= models.IntegerField(default=-1) 	# user id
    cost 			= models.IntegerField(default=10)
	parking_time 	= models.DateTimeField() #  max 30 minutes from the offering time
	status 			= models.CharField(max_length=200, default="available") # available, in process, done, canceled irrelevent etc.
   	parking_rate 	= models.DecimalField(max_digits = 3, decimal_places=3, default=-1) #distance between target address and parking address. 
	target_address 	= models.CharField(max_length=200) #coordinates of target address. (x,y)
	parking_address = models.CharField(max_length=200) #coordinates of parking address. (x,y)
	lock 			= threading.Lock()
	cond 			= threading.Condition(threading.Lock())
	pin_code		= models.IntegerField(default=-1)

	def wait_lock(self, timeout):
	    with self.cond:
	        current_time = start_time = time.time()
	        while current_time < start_time + timeout:
	            if self.lock.acquire(False):
	                return True
	            else:
	                self.cond.wait(timeout - current_time + start_time)
	                current_time = time.time()
	    return False

