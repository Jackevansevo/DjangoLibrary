# -*- coding: utf-8 -*-
# Generated by Django 1.10.5 on 2017-01-27 11:02
from __future__ import unicode_literals

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('books', '0005_auto_20170127_1013'),
    ]

    operations = [
        migrations.AlterField(
            model_name='customerbook',
            name='customer',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='books', to=settings.AUTH_USER_MODEL),
        ),
    ]
