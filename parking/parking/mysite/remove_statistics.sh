import sys
from django.contrib.auth import authenticate
from django.contrib.auth import get_user_model
from polls.models import Statistics

#remove all dummy purcahses
	
stats = Statistics.objects.all()
i = 0
try:

	for stat in stats:
		i+=1
		if (i%100 ==0):
			print(str(i))
		stat.delete()

except Statistics.DoesNotExist:
	pass

