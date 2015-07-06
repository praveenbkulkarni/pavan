# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('myapp', '0006_auto_20150629_1547'),
    ]

    operations = [
        migrations.AddField(
            model_name='paths',
            name='company_path',
            field=models.CharField(default='', max_length=255),
            preserve_default=True,
        ),
    ]
