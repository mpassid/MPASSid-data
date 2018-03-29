
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
import authdata.models
import authdata.forms
from authdata.tests import factories as f


class TestUserCreationForm(TestCase):

  def test_clean_username(self):
    obj = authdata.forms.UserCreationForm({'username': 'foo'})
    self.assertTrue(obj.is_valid())
    username = obj.clean_username()
    self.assertEqual(username, 'foo')

  def test_clean_username_error_duplicate(self):
    f.UserFactory(username='foo')
    obj = authdata.forms.UserCreationForm({'username': 'foo'})
    self.assertFalse(obj.is_valid())
    self.assertEqual(obj.errors, {'username': [u'A user with that username already exists.']})

  def test_save(self):
    self.assertEqual(authdata.models.User.objects.count(), 0)
    obj = authdata.forms.UserCreationForm({'username': 'foo'})
    self.assertTrue(obj.is_valid())
    user = obj.save(commit=True)
    self.assertTrue(user)
    self.assertEqual(authdata.models.User.objects.count(), 1)


class TestUserChangeForm(TestCase):

  def test_clean_password(self):
    user_obj = f.UserFactory(username='foo', password='originalpass1')
    obj = authdata.forms.UserChangeForm({'password': 'bar'}, instance=user_obj)
    password = obj.clean_password()
    self.assertEqual(password, 'originalpass1')


# vim: tabstop=2 expandtab shiftwidth=2 softtabstop=2

