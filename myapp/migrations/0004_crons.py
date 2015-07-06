# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('myapp', '0003_picturetables_status'),
    ]

    operations = [
        migrations.CreateModel(
            name='crons',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('cronName', models.CharField(max_length=20)),
                ('domainName', models.CharField(max_length=20)),
                ('tablename', models.CharField(max_length=100)),
                ('svmnames', models.CharField(max_length=100)),
                ('fetchenddate', models.DateTimeField(auto_now_add=True)),
                ('fetchstartdate', models.DateTimeField(auto_now_add=True)),
                ('isactive', models.IntegerField()),
                ('status', models.IntegerField()),
            ],
            options={
            },
            bases=(models.Model,),
        ),
    ]
