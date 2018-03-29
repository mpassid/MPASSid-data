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

import csv
import codecs
from optparse import make_option
from collections import OrderedDict
from django.core.management.base import BaseCommand, CommandError
from django.db import IntegrityError
from django.core.exceptions import ObjectDoesNotExist
from authdata.models import User, Role, Attribute, UserAttribute, Municipality, School, Attendance, Source


class Command(BaseCommand):
  help = """Imports data from CSV file to the database.
Do not put any header to the CSV file. Only provide data separated by commas and quoted with \".

You need to provide at least two arguments: the name of the input file and list of attributes for the User.

For example: manage.py csv_import file.csv dreamschool,facebook,twitter,linkedin,mepin
"""
  args = '<csvfile> <attr1,attr2...>'
  option_list = BaseCommand.option_list + (
    make_option('--source',
        action='store',
        dest='source',
        default='manual',
        help='Source value for this run'),
    make_option('--municipality',
        action='store',
        dest='municipality',
        default='-',
        help='Source value for this run'),
    make_option('--run',
        action='store_true',
        dest='really_do_this',
        default=False,
        help='Really run the command'),
    make_option('--verbose',
        action='store_true',
        dest='verbose',
        default=False,
        help='Verbose'),
  )

  def handle(self, *args, **options):
    if len(args) != 2:
      raise CommandError('Wrong parameters, try reading --help')
    self.verbose = options['verbose']
    self.municipality = options['municipality']
    # Create needed Attribute objects to the database
    # These are the attributes which can be used to query for User objects in the API
    # attribute names are defined in the commandline as the second parameter
    # for example: manage.py csv_import file.csv dreamschool,facebook,twitter,linkedin,mepin
    self.attribute_names = OrderedDict()
    for key in args[1].split(','):
      self.attribute_names[key], _ = Attribute.objects.get_or_create(name=key)
    self.source, _ = Source.objects.get_or_create(name=options['source'])
    # If you need more roles, add them here
    self.role_names = OrderedDict()
    for r in ['teacher', 'student']:
      self.role_names[r], _ = Role.objects.get_or_create(name=r)

    csv_data = csv.reader(codecs.open(args[0], 'rb'), delimiter=',', quotechar='"')
    for r in csv_data:
      # These are the fixed fields for the User. These are returned from the API.
      data = {
        'username': r[0],  # OID
        'school': r[1],  # School
        'group': r[2],  # Class
        'role': r[3],  # Role
        'first_name': r[4],  # First name
        'last_name': r[5],  # Last name
      }

      # This is not mandatory, but it would be nice. Can be changed to error by terminating the script here.
      if data['role'] not in self.role_names.keys():
        print 'WARNING, role not in:', repr(self.role_names.keys())

      attributes = {}
      i = 6  # Next csv_data row index is 6 :)
      for a in self.attribute_names:
        attributes[a] = r[i]
        i = i + 1

      try:
        if self.verbose:
          print repr(data)
          print repr(attributes)
        if options['really_do_this']:
          self.really_do_this(data.copy(), attributes.copy())
      except IntegrityError, e:
        print "ERR IE", e
        print repr(data)
        print repr(attributes)
      except ObjectDoesNotExist, e:
        print "ERR ODN", e
        print repr(data)
        print repr(attributes)

  def really_do_this(self, d, a):
    # Create User
    # User is identified from username and other fields are updated
    user, _ = User.objects.get_or_create(username=d['username'])
    user.first_name = d['first_name']
    user.last_name = d['last_name']
    user.save()

    # Assign attributes for User
    # There can be multiple attributes with the same name and different value.
    # This is one of the reasons we have the source parameter to tell where the data came from.
    for k, v in a.iteritems():
      UserAttribute.objects.get_or_create(user=user, attribute=self.attribute_names[k], value=v, source=self.source)

    # Create Municipality
    # If you leave this empty on the CLI it will default to '-'
    municipality, _ = Municipality.objects.get_or_create(name=self.municipality)

    # Create School
    # School data is not updated after it is created. Data can be then changed in the admin.
    school, _ = School.objects.get_or_create(school_id=d['school'], defaults={'municipality': municipality, 'name': d['school']})

    # Create Attendance object for User. There can be more than one Attendance per User.
    Attendance.objects.get_or_create(user=user, school=school, role=self.role_names[d['role']], group=d['group'], source=self.source)

# vim: tabstop=2 expandtab shiftwidth=2 softtabstop=2

