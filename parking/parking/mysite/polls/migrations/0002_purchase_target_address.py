# -*- coding: utf-8 -*-
# Generated by Django 1.11.7 on 2018-01-14 11:26
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('polls', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='purchase',
            name='target_address',
            field=models.CharField(default='messi', max_length=2000),
        ),
    ]
