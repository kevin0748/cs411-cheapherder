# -*- coding: utf-8 -*-
# Generated by Django 1.11.7 on 2017-11-15 06:52
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('CheapHerder', '0014_auto_20171114_2159'),
    ]

    operations = [
        migrations.AddField(
            model_name='group',
            name='is_open',
            field=models.BooleanField(default=True),
        ),
    ]