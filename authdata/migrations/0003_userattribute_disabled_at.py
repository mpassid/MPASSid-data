# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('authdata', '0002_municipality_municipality_id'),
    ]

    operations = [
        migrations.AddField(
            model_name='userattribute',
            name='disabled_at',
            field=models.DateTimeField(null=True, blank=True),
            preserve_default=True,
        ),
    ]
