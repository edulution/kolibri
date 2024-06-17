# -*- coding: utf-8 -*-
# Generated by Django 1.11.29 on 2023-10-17 23:41
from __future__ import unicode_literals

import django.db.models.deletion
import django.utils.timezone
import morango.models.fields.uuids
from django.conf import settings
from django.db import migrations
from django.db import models


class Migration(migrations.Migration):

    dependencies = [
        ("kolibriauth", "0001_initial"),
        ("discovery", "0012_remove_pinned_device"),
    ]

    operations = [
        migrations.CreateModel(
            name="PinnedDevice",
            fields=[
                (
                    "id",
                    models.AutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                ("instance_id", morango.models.fields.uuids.UUIDField()),
                (
                    "created",
                    models.DateTimeField(
                        db_index=True, default=django.utils.timezone.now
                    ),
                ),
                (
                    "user",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        to="kolibriauth.FacilityUser",
                    ),
                ),
            ],
        ),
        migrations.AlterUniqueTogether(
            name="pinneddevice",
            unique_together=set([("user", "instance_id")]),
        ),
    ]