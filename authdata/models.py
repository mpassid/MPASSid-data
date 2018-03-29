
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

import logging
from django.db import models
from django.contrib.auth.models import AbstractUser

LOG = logging.getLogger(__name__)


class TimeStampedModel(models.Model):
  created = models.DateTimeField(auto_now_add=True)
  modified = models.DateTimeField(auto_now=True)

  class Meta:
    abstract = True


class User(TimeStampedModel, AbstractUser):
  external_source = models.CharField(max_length=2000, blank=True, default='')
  external_id = models.CharField(max_length=2000, blank=True, default='')

  def __unicode__(self):
    return self.username


class Source(TimeStampedModel):
  name = models.CharField(max_length=2048)

  def __unicode__(self):
    return self.name


class Municipality(TimeStampedModel):
  name = models.CharField(max_length=2048)
  municipality_id = models.CharField(max_length=2048)
  data_source = models.ForeignKey(Source)

  def __unicode__(self):
    return self.name


class School(TimeStampedModel):
  name = models.CharField(max_length=2048)
  school_id = models.CharField(max_length=2048)
  municipality = models.ForeignKey(Municipality, related_name='schools')
  data_source = models.ForeignKey(Source)

  def __unicode__(self):
    return "%s / %s" % (self.name, self.municipality)


class Attribute(TimeStampedModel):
  name = models.CharField(max_length=2048, blank=True, null=True, default=None)

  def __unicode__(self):
    return self.name


class UserAttribute(TimeStampedModel):
  user = models.ForeignKey(User, related_name='attributes')
  attribute = models.ForeignKey(Attribute)
  value = models.CharField(max_length=2048, blank=True, null=True, default=None)
  data_source = models.ForeignKey(Source)
  disabled_at = models.DateTimeField(null=True, blank=True)

  def __unicode__(self):
    return u'%s: %s' % (self.attribute, self.value)


class Role(TimeStampedModel):
  name = models.CharField(max_length=2048)

  def __unicode__(self):
    return self.name


class Attendance(TimeStampedModel):
  user = models.ForeignKey(User, related_name='attendances')
  school = models.ForeignKey(School, related_name='users')
  role = models.ForeignKey(Role)
  group = models.CharField(max_length=2048, blank=True, default='')
  data_source = models.ForeignKey(Source, related_name='attendances')

  def __unicode__(self):
    return u'%s: %s / %s' % (self.role, self.school.name, self.school.municipality.name)


# vim: tabstop=2 expandtab shiftwidth=2 softtabstop=2

