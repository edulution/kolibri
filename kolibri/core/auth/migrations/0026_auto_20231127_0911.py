# -*- coding: utf-8 -*-
# Generated by Django 1.11.29 on 2023-11-27 03:41
from __future__ import unicode_literals

from django.db import migrations
import kolibri.core.fields


class Migration(migrations.Migration):

    dependencies = [
        ('kolibriauth', '0025_collection_subscriptions'),
    ]

    operations = [
        migrations.AlterField(
            model_name='collection',
            name='subscriptions',
            field=kolibri.core.fields.JSONField(blank=True, default='[]'),
        ),
    ]
