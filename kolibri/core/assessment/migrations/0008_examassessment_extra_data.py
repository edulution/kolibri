# -*- coding: utf-8 -*-
# Generated by Django 1.11.29 on 2024-05-02 19:01
from __future__ import unicode_literals

from django.db import migrations
import kolibri.core.fields


class Migration(migrations.Migration):

    dependencies = [
        ('assessment', '0007_auto_20240502_2023'),
    ]

    operations = [
        migrations.AddField(
            model_name='examassessment',
            name='extra_data',
            field=kolibri.core.fields.JSONField(blank=True, default=[]),
        ),
    ]