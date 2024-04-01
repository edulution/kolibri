# -*- coding: utf-8 -*-
# Generated by Django 1.11.29 on 2024-03-22 12:02
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('notifications', '0005_learnerprogressnotification_assignment_collections'),
    ]

    operations = [
        migrations.AlterField(
            model_name='learnerprogressnotification',
            name='notification_object',
            field=models.CharField(blank=True, choices=[('Assessment', 'Assessment'), ('Help', 'Help'), ('Lesson', 'Lesson'), ('Quiz', 'Quiz'), ('Resource', 'Resource')], max_length=200),
        ),
    ]