# -*- coding: utf-8 -*-
# Generated by Django 1.11.29 on 2022-10-25 04:10
from __future__ import unicode_literals

import django.core.validators
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('api', '0009_auto_20221025_0330'),
    ]

    operations = [
        migrations.AlterField(
            model_name='breed',
            name='name',
            field=models.CharField(max_length=30, validators=[django.core.validators.RegexValidator(regex='^[a-zA-Z0-9 ]+$')]),
        ),
        migrations.AlterField(
            model_name='dog',
            name='name',
            field=models.CharField(max_length=30, validators=[django.core.validators.RegexValidator(regex='^[a-zA-Z0-9 ]+$')]),
        ),
    ]