# -*- coding: utf-8 -*-
# Generated by Django 1.11.5 on 2017-10-19 01:21
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('badicv', '0003_auto_20171018_2148'),
    ]

    operations = [
        migrations.AddField(
            model_name='experience',
            name='location',
            field=models.CharField(default='DEFAULT LOCATION PLEASE REMOVE', max_length=64),
        ),
        migrations.AlterField(
            model_name='experiencewithskill',
            name='description',
            field=models.TextField(default='DEFAULT DESCRIPTION PLEASE REMOVE'),
        ),
    ]
