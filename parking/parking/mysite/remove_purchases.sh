import sys
from django.contrib.auth import authenticate
from django.contrib.auth import get_user_model
from polls.models import Purchase

#remove all dummy purcahses
DUMMY_ADDRESS 	= "dummy address" 	
dummy_purchases = Purchase.objects.filter(parking_address = DUMMY_ADDRESS)

try:
	for spot in dummy_purchases:
		spot.delete()

except Purchase.DoesNotExist:
	pass

