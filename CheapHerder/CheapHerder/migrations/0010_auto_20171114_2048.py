# -*- coding: utf-8 -*-
# Generated by Django 1.11.5 on 2017-11-14 20:48
from __future__ import unicode_literals

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('CheapHerder', '0009_auto_20171112_1529'),
    ]

    operations = [
        migrations.RenameField(
            model_name='product',
            old_name='attributes',
            new_name='gross_weight',
        ),
        migrations.RenameField(
            model_name='product',
            old_name='sku',
            new_name='item_code',
        ),
        migrations.RenameField(
            model_name='product',
            old_name='brand',
            new_name='package_size',
        ),
        migrations.RenameField(
            model_name='product',
            old_name='inventory',
            new_name='product_name',
        ),
        migrations.RenameField(
            model_name='product',
            old_name='colors',
            new_name='quantity',
        ),
        migrations.RenameField(
            model_name='product_price',
            old_name='sku',
            new_name='item_code',
        ),
        migrations.RemoveField(
            model_name='product',
            name='category_id',
        ),
        migrations.RemoveField(
            model_name='product',
            name='materials',
        ),
        migrations.RemoveField(
            model_name='product',
            name='p_type',
        ),
        migrations.RemoveField(
            model_name='product',
            name='subcategory',
        ),
        migrations.RemoveField(
            model_name='product',
            name='subcategory_id',
        ),
        migrations.RemoveField(
            model_name='product',
            name='tags',
        ),
        migrations.RemoveField(
            model_name='product',
            name='unit_weight',
        ),
        migrations.RemoveField(
            model_name='product',
            name='upc',
        ),
        migrations.AlterField(
            model_name='product',
            name='supplier_id',
            field=models.ForeignKey(blank=True, on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL),
        ),
    ]
