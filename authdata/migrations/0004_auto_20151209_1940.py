# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('authdata', '0003_userattribute_disabled_at'),
    ]

    operations = [
        migrations.AddField(
            model_name='user',
            name='external_id',
            field=models.CharField(default=b'', max_length=2000, blank=True),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='user',
            name='external_source',
            field=models.CharField(default=b'', max_length=2000, blank=True),
            preserve_default=True,
        ),
    ]
