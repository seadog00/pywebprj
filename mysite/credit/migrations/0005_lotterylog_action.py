# -*- coding: utf-8 -*-
# Generated by Django 1.10.3 on 2016-12-17 08:58
from __future__ import unicode_literals

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('credit', '0004_myrewards_action'),
    ]

    operations = [
        migrations.AddField(
            model_name='lotterylog',
            name='action',
            field=models.ForeignKey(default=1, on_delete=django.db.models.deletion.CASCADE, to='credit.Actions', verbose_name='\u6d3b\u52a8'),
            preserve_default=False,
        ),
    ]
