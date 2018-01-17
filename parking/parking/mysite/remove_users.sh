import sys
from django.contrib.auth import authenticate
from django.contrib.auth import get_user_model
User = get_user_model()

#remove all dummy users
LAST_NAME = "lastName"
dummy_users = User.objects.filter(last_name = LAST_NAME)

try:
	for user in dummy_users:
		user.delete()

except Users.DoesNotExist:
	pass

