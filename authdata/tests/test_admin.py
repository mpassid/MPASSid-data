
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

from mock import Mock
from django.test import TestCase
from authdata import admin


class TestAdmin(TestCase):

  def test_municipality(self):
    obj = admin.MunicipalityAdmin(Mock(), Mock())
    self.assertTrue(obj)

  def test_school(self):
    obj = admin.SchoolAdmin(Mock(), Mock())
    self.assertTrue(obj)

  def test_attendance(self):
    obj = admin.AttendanceAdmin(Mock(), Mock())
    self.assertTrue(obj)

  def test_attribute(self):
    obj = admin.AttributeAdmin(Mock(), Mock())
    self.assertTrue(obj)

  def test_userattribute(self):
    obj = admin.UserAttributeAdmin(Mock(), Mock())
    self.assertTrue(obj)

  def test_source(self):
    obj = admin.SourceAdmin(Mock(), Mock())
    self.assertTrue(obj)

  def test_user(self):
    obj = admin.UserAdmin(Mock(), Mock())
    self.assertTrue(obj)


# vim: tabstop=2 expandtab shiftwidth=2 softtabstop=2

