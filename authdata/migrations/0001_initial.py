# -*- encoding: utf-8 -*-

# The MIT License (MIT)
#
# Copyright (c) 2014-2015 Haltu Oy, http://haltu.fi
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in
# all copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN
# THE SOFTWARE.
#

from __future__ import unicode_literals

from django.db import models, migrations
import django.utils.timezone
from django.conf import settings
import django.core.validators


class Migration(migrations.Migration):

    dependencies = [
        ('auth', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='User',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('password', models.CharField(max_length=128, verbose_name='password')),
                ('last_login', models.DateTimeField(default=django.utils.timezone.now, verbose_name='last login')),
                ('is_superuser', models.BooleanField(default=False, help_text='Designates that this user has all permissions without explicitly assigning them.', verbose_name='superuser status')),
                ('username', models.CharField(help_text='Required. 30 characters or fewer. Letters, digits and @/./+/-/_ only.', unique=True, max_length=30, verbose_name='username', validators=[django.core.validators.RegexValidator('^[\\w.@+-]+$', 'Enter a valid username.', 'invalid')])),
                ('first_name', models.CharField(max_length=30, verbose_name='first name', blank=True)),
                ('last_name', models.CharField(max_length=30, verbose_name='last name', blank=True)),
                ('email', models.EmailField(max_length=75, verbose_name='email address', blank=True)),
                ('is_staff', models.BooleanField(default=False, help_text='Designates whether the user can log into this admin site.', verbose_name='staff status')),
                ('is_active', models.BooleanField(default=True, help_text='Designates whether this user should be treated as active. Unselect this instead of deleting accounts.', verbose_name='active')),
                ('date_joined', models.DateTimeField(default=django.utils.timezone.now, verbose_name='date joined')),
                ('created', models.DateTimeField(default=django.utils.timezone.now, auto_now_add=True)),
                ('modified', models.DateTimeField(default=django.utils.timezone.now, auto_now=True)),
                ('groups', models.ManyToManyField(related_query_name='user', related_name='user_set', to='auth.Group', blank=True, help_text='The groups this user belongs to. A user will get all permissions granted to each of his/her group.', verbose_name='groups')),
                ('user_permissions', models.ManyToManyField(related_query_name='user', related_name='user_set', to='auth.Permission', blank=True, help_text='Specific permissions for this user.', verbose_name='user permissions')),
            ],
            options={
                'abstract': False,
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='Attendance',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('created', models.DateTimeField(default=django.utils.timezone.now, auto_now_add=True)),
                ('modified', models.DateTimeField(default=django.utils.timezone.now, auto_now=True)),
                ('group', models.CharField(default=b'', max_length=2048, blank=True)),
            ],
            options={
                'abstract': False,
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='Attribute',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('created', models.DateTimeField(default=django.utils.timezone.now, auto_now_add=True)),
                ('modified', models.DateTimeField(default=django.utils.timezone.now, auto_now=True)),
                ('name', models.CharField(default=None, max_length=2048, null=True, blank=True)),
            ],
            options={
                'abstract': False,
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='Municipality',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('created', models.DateTimeField(default=django.utils.timezone.now, auto_now_add=True)),
                ('modified', models.DateTimeField(default=django.utils.timezone.now, auto_now=True)),
                ('name', models.CharField(max_length=2048)),
            ],
            options={
                'abstract': False,
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='Role',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('created', models.DateTimeField(default=django.utils.timezone.now, auto_now_add=True)),
                ('modified', models.DateTimeField(default=django.utils.timezone.now, auto_now=True)),
                ('name', models.CharField(max_length=2048)),
            ],
            options={
                'abstract': False,
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='School',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('created', models.DateTimeField(default=django.utils.timezone.now, auto_now_add=True)),
                ('modified', models.DateTimeField(default=django.utils.timezone.now, auto_now=True)),
                ('name', models.CharField(max_length=2048)),
                ('school_id', models.CharField(max_length=2048)),
            ],
            options={
                'abstract': False,
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='Source',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('created', models.DateTimeField(default=django.utils.timezone.now, auto_now_add=True)),
                ('modified', models.DateTimeField(default=django.utils.timezone.now, auto_now=True)),
                ('name', models.CharField(max_length=2048)),
            ],
            options={
                'abstract': False,
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='UserAttribute',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('created', models.DateTimeField(default=django.utils.timezone.now, auto_now_add=True)),
                ('modified', models.DateTimeField(default=django.utils.timezone.now, auto_now=True)),
                ('value', models.CharField(default=None, max_length=2048, null=True, blank=True)),
                ('attribute', models.ForeignKey(to='authdata.Attribute')),
                ('data_source', models.ForeignKey(to='authdata.Source')),
                ('user', models.ForeignKey(related_name=b'attributes', to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'abstract': False,
            },
            bases=(models.Model,),
        ),
        migrations.AddField(
            model_name='school',
            name='data_source',
            field=models.ForeignKey(to='authdata.Source'),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='school',
            name='municipality',
            field=models.ForeignKey(related_name=b'schools', to='authdata.Municipality'),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='municipality',
            name='data_source',
            field=models.ForeignKey(to='authdata.Source'),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='attendance',
            name='data_source',
            field=models.ForeignKey(related_name=b'attendances', to='authdata.Source'),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='attendance',
            name='role',
            field=models.ForeignKey(to='authdata.Role'),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='attendance',
            name='school',
            field=models.ForeignKey(related_name=b'users', to='authdata.School'),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='attendance',
            name='user',
            field=models.ForeignKey(related_name=b'attendances', to=settings.AUTH_USER_MODEL),
            preserve_default=True,
        ),
    ]
