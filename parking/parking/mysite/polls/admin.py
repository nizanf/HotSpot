# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.contrib import admin
from django.contrib.auth.models import User
from .models import Profile, Purchase, FreeSpot, Statistics

# Register your models here.

admin.site.register(Profile)
admin.site.register(Purchase)
admin.site.register(FreeSpot)
admin.site.register(Statistics)
