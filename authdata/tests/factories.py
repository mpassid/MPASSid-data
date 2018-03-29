
# -*- coding: utf-8 -*-

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
# pylint: disable=locally-disabled, no-member, unused-argument, no-init, old-style-class, too-few-public-methods, unnecessary-lambda


import string
import factory
import factory.fuzzy
from django.utils import timezone
from authdata import models


class SourceFactory(factory.django.DjangoModelFactory):
  class Meta:
    model = models.Source

  name = 'autogentest'


class UserFactory(factory.django.DjangoModelFactory):
  class Meta:
    model = models.User

  first_name = factory.Sequence(lambda n: 'First{0}'.format(n))
  last_name = factory.Sequence(lambda n: 'Last{0}'.format(n))
  last_login = timezone.now()
  email = factory.LazyAttribute(lambda u:
      '{0}.{1}@example.com'.format(u.first_name, u.last_name))
  username = factory.fuzzy.FuzzyText(length=11, chars=string.digits, prefix='1.2.246.562.24.')


class MunicipalityFactory(factory.django.DjangoModelFactory):
  class Meta:
    model = models.Municipality

  name = factory.Sequence(lambda n: 'Municipality{0}'.format(n))
  municipality_id = factory.fuzzy.FuzzyText(length=7, chars=string.digits, suffix='-8')
  data_source = factory.SubFactory(SourceFactory)


class SchoolFactory(factory.django.DjangoModelFactory):
  class Meta:
    model = models.School

  name = factory.Sequence(lambda n: 'School{0}'.format(n))
  school_id = factory.Sequence(lambda n: '{0}'.format(n))
  municipality = factory.SubFactory(MunicipalityFactory)
  data_source = factory.SubFactory(SourceFactory)


class AttributeFactory(factory.django.DjangoModelFactory):
  class Meta:
    model = models.Attribute

  name = factory.Sequence(lambda n: 'attribute{0}'.format(n))


class UserAttributeFactory(factory.django.DjangoModelFactory):
  class Meta:
    model = models.UserAttribute

  user = factory.SubFactory(UserFactory)
  attribute = factory.SubFactory(AttributeFactory)
  value = factory.fuzzy.FuzzyText(length=10)
  data_source = factory.SubFactory(SourceFactory)


class RoleFactory(factory.django.DjangoModelFactory):
  class Meta:
    model = models.Role

  name = factory.Sequence(lambda n: 'Role{0}'.format(n))


class AttendanceFactory(factory.django.DjangoModelFactory):
  class Meta:
    model = models.Attendance

  user = factory.SubFactory(UserFactory)
  school = factory.SubFactory(SchoolFactory)
  role = factory.SubFactory(RoleFactory)
  group = factory.Sequence(lambda n: 'Group{0}'.format(n))
  data_source = factory.SubFactory(SourceFactory)


# vim: tabstop=2 expandtab shiftwidth=2 softtabstop=2

