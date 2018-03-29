
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
# pylint: disable=locally-disabled, no-member

from django.test import TestCase
from authdata.tests import factories as f
from authdata import models


class TestUser(TestCase):

  def test_user(self):
    o = f.UserFactory()
    self.assertTrue(o)
    self.assertTrue(unicode(o) == o.username)
    u = models.User.objects.create(username='foo')
    u.email = 'foo@bar.com'
    u.save()
    self.assertTrue(u.email)

  def test_user_timestamps(self):
    u = f.UserFactory()
    self.assertTrue(u.created)
    self.assertTrue(u.modified)

  def test_user_last_login(self):
    u = f.UserFactory()
    self.assertTrue(u.last_login)

  def test_user_external_fields(self):
    u = f.UserFactory()
    self.assertFalse(u.external_source)
    self.assertFalse(u.external_id)


class TestSource(TestCase):
  def test_source(self):
    o = f.SourceFactory(name=u'Ääkköstesti')
    self.assertTrue(o)
    self.assertTrue(unicode(o), o.__unicode__())
    self.assertTrue(str(o))
    self.assertTrue(o.name)
    self.assertTrue(o.created)
    self.assertTrue(o.modified)


class TestMunicipality(TestCase):
  def test_municipality(self):
    o = f.MunicipalityFactory(name=u'Ääkköstesti')
    self.assertTrue(o)
    self.assertTrue(o.name)
    self.assertTrue(unicode(o) == o.name)
    self.assertTrue(o.created)
    self.assertTrue(o.modified)


class TestSchool(TestCase):
  def test_school(self):
    o = f.SchoolFactory(name=u'Ääkköstesti', municipality__name=u'Ääkköskunta')
    self.assertTrue(o)
    self.assertTrue(o.name)
    self.assertIn(o.name, unicode(o))
    self.assertIn(o.municipality.name, unicode(o))
    self.assertTrue(o.created)
    self.assertTrue(o.modified)


class TestAttribute(TestCase):
  def test_attribute(self):
    o = f.AttributeFactory(name=u'Ääkköstesti')
    self.assertTrue(o)
    self.assertTrue(o.name)
    self.assertTrue(unicode(o) == o.name)
    self.assertTrue(o.created)
    self.assertTrue(o.modified)


class TestUserAttribute(TestCase):
  def test_userattribute(self):
    o = f.UserAttributeFactory(attribute__name=u'Ääkkösattribute',
                               value=u'Ääkkösvalue')
    self.assertTrue(o)
    self.assertTrue(o.value)
    self.assertTrue(o.created)
    self.assertTrue(o.modified)
    self.assertIn(u'Ääkkösattribute', unicode(o))
    self.assertIn(u'Ääkkösvalue', unicode(o))


class TestRole(TestCase):
  def test_role(self):
    o = f.RoleFactory(name=u'Ääkkösrooli')
    self.assertTrue(o)
    self.assertTrue(o.name)
    self.assertTrue(unicode(o) == o.name)
    self.assertTrue(o.created)
    self.assertTrue(o.modified)


class TestAttendance(TestCase):
  def test_attendance(self):
    o = f.AttendanceFactory(school__name=u'Ääkkösschool',
        school__municipality__name=u'Ääkkösmunicipality',
        role__name=u'Ääkkösrole', group=u'Ääkkösgroup')
    self.assertTrue(o)
    self.assertTrue(o.created)
    self.assertTrue(o.modified)
    self.assertIn(u'Ääkkösschool', unicode(o))
    self.assertIn(u'Ääkkösrole', unicode(o))
    self.assertIn(u'Ääkkösmunicipality', unicode(o))


class TestTimeStampedModel(TestCase):
  def test_timestampedmodel(self):
    o = models.TimeStampedModel()
    self.assertTrue(o.created is None)
    self.assertTrue(o.modified is None)

# vim: tabstop=2 expandtab shiftwidth=2 softtabstop=2

