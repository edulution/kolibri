# -*- coding: utf-8 -*-
# Generated by Django 1.11.20 on 2022-07-29 12:57
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('kolibriauth', '0014_collection_subscriptions'),
    ]

    operations = [
        migrations.AddField(
            model_name='facilityuser',
            name='deleted',
            field=models.BooleanField(default=False),
        ),
    ]
