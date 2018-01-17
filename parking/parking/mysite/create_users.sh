import sys
from django.contrib.auth import authenticate
from django.contrib.auth import get_user_model
User = get_user_model()

NUM_OF_USERS = 10
BUYER_NAME = "buyer"
SELLER_NAME = "seller"
PASSWORD = "Aa123456"
LAST_NAME = "lastName"
PHONE_NUM = "0545000111"

bNames = []
sNames = []
sEmails = []
bEmails = []

for i in range(0,NUM_OF_USERS):
	bNames.append(BUYER_NAME+str(i))
	sNames.append(SELLER_NAME+str(i))	
	bEmails.append(bNames[i] + "@gmail.com")
	sEmails.append(sNames[i] + "@gmail.com")

for i in range(0,NUM_OF_USERS):
	# create new user
	new_buyer = User.objects.create_user(username=bNames[i],password = PASSWORD, email = bEmails[i], first_name = bNames[i], last_name = LAST_NAME)

	new_buyer.profile.phone_number = PHONE_NUM
	# new_buyer.profile.rating = 5
	new_buyer.save()

	new_seller = User.objects.create_user(username=sNames[i], \
			password = PASSWORD, email = sEmails[i], \
			first_name = sNames[i], last_name = LAST_NAME)

	new_seller.profile.phone_number = PHONE_NUM
	new_seller.save()
