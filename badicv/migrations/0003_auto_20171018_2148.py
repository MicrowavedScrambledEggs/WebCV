# -*- coding: utf-8 -*-
# Generated by Django 1.11.5 on 2017-10-18 08:48
from __future__ import unicode_literals

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('badicv', '0002_experiencetoskill_description'),
    ]

    operations = [
        migrations.RenameModel(
            old_name='ExperienceToSkill',
            new_name='ExperienceWithSkill',
        ),
    ]
