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
#

import sys
import random
from django.core.management.base import BaseCommand
from authdata.models import User, Role, Attribute, UserAttribute, Municipality, School, Attendance, Source
from authdata.tests import factories as f


class Command(BaseCommand):
  help = """
  Creates a set of test data:

  * 10000 users, random-generated username in OID format
  * 10 municipalities
  * 100 schools
  * either "teacher" or "student" role in municipality
  * varying number (1-10) of groups for each user
  """

  def handle(self, *args, **options):
    source = f.SourceFactory.create()
    attributes = f.AttributeFactory.create_batch(10)
    roles = [Role.objects.get_or_create(name='teacher'), Role.objects.get_or_create(name='student')]
    for m in xrange(10):
      muni = f.MunicipalityFactory.create(data_source=source)
      schools = f.SchoolFactory.create_batch(10, municipality=muni, data_source=source)
      for u in xrange(1000):
        user = f.UserFactory()
        role = random.choice(roles)
        for attr in attributes:
          f.UserAttributeFactory.create(user=user, attribute=attr, data_source=source)
        for g in xrange(random.randint(1, 10)):
          f.AttendanceFactory(user=user, school=random.choice(schools), role=role, data_source=source)
        sys.stdout.write('.')
        sys.stdout.flush()
    sys.stdout.write('\n')

# vim: tabstop=2 expandtab shiftwidth=2 softtabstop=2

