# -*- coding: utf-8 -*-
# Generated by Django 1.11.5 on 2017-12-06 18:58
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('CheapHerder', '0031_message_text'),
    ]

    operations = [
        migrations.AddField(
            model_name='payment',
            name='status',
            field=models.CharField(default=1, max_length=200),
            preserve_default=False,
        ),
    ]
