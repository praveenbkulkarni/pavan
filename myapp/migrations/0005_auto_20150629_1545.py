# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('myapp', '0004_crons'),
    ]

    operations = [
        migrations.AddField(
            model_name='crons',
            name='fetchtime',
            field=models.DateTimeField(default='2015-01-01', auto_now_add=True),
            preserve_default=True,
        ),
    ]
