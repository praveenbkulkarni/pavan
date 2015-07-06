# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('myapp', '0002_auto_20150617_1607'),
    ]

    operations = [
        migrations.AddField(
            model_name='picturetables',
            name='status',
            field=models.IntegerField(default=0),
            preserve_default=True,
        ),
    ]
