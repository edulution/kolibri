# -*- coding: utf-8 -*-
# Generated by Django 1.11.29 on 2024-04-01 14:06
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('assessment', '0004_auto_20240401_1026'),
    ]

    operations = [
        migrations.AddField(
            model_name='examassessment',
            name='channel_id',
            field=models.UUIDField(null=True),
        ),
        migrations.AddField(
            model_name='examassessmentgroup',
            name='channel_id',
            field=models.UUIDField(null=True),
        ),
    ]
