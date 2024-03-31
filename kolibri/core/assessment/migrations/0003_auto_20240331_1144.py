# -*- coding: utf-8 -*-
# Generated by Django 1.11.29 on 2024-03-31 06:14
from __future__ import unicode_literals

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion
import kolibri.core.fields
import morango.models.fields.uuids


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('kolibriauth', '0026_auto_20231127_0911'),
        ('assessment', '0002_examassessment_assignments'),
    ]

    operations = [
        migrations.CreateModel(
            name='ExamAssessmentGroup',
            fields=[
                ('id', morango.models.fields.uuids.UUIDField(editable=False, primary_key=True, serialize=False)),
                ('_morango_dirty_bit', models.BooleanField(default=True, editable=False)),
                ('_morango_source_id', models.CharField(editable=False, max_length=96)),
                ('_morango_partition', models.CharField(editable=False, max_length=128)),
                ('title', models.CharField(max_length=200)),
                ('learner_id', models.IntegerField(default=1)),
                ('active', models.BooleanField(default=False)),
                ('date_activated', models.DateTimeField(blank=True, default=None, null=True)),
                ('date_created', models.DateTimeField(auto_now_add=True, null=True)),
                ('archive', models.BooleanField(default=False)),
                ('date_archived', models.DateTimeField(blank=True, default=None, null=True)),
                ('assessment_map', kolibri.core.fields.JSONField(blank=True, default=[])),
                ('creator', models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, related_name='assessementfacilityuser', to=settings.AUTH_USER_MODEL)),
                ('current_assessment', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='current_assessment_group', to='assessment.ExamAssessment')),
                ('dataset', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='kolibriauth.FacilityDataset')),
                ('last_assessment', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='last_assessment_group', to='assessment.ExamAssessment')),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.AddField(
            model_name='examassessment',
            name='assessment_group',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='exam_assessments', to='assessment.ExamAssessmentGroup'),
        ),
    ]
