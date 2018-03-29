
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
# pylint: disable=locally-disabled, no-member, unused-argument

import mock
import requests

from rest_framework.test import APIRequestFactory
from rest_framework.test import APITestCase
from rest_framework.test import force_authenticate

import django.http
from django.test import override_settings

import authdata.models
import authdata.views
import authdata.datasources.dreamschool
from authdata.tests import factories as f


AUTH_EXTERNAL_SOURCES = {
    'ldap_test': ['authdata.datasources.ldap_base', 'TestLDAPDataSource', {
        'host': 'ldaps://1.2.3.4',
        'username': 'uid=foo,ou=Bar,dc=zap,dc=csc,dc=fi',
        'password': 'password'
    }],
    'dreamschool': ['authdata.datasources.dreamschool', 'DreamschoolDataSource', {
        'api_url': 'https://foo.fi/api/2/user/',
        'username': 'username',
        'password': 'password',
    }],
}

AUTH_EXTERNAL_ATTRIBUTE_BINDING = {
    'ldap_test': 'ldap_test',
    'dreamschool': 'dreamschool',
}

AUTH_EXTERNAL_MUNICIPALITY_BINDING = {
    'Foo': 'ldap_test',
    'Bar': 'dreamschool',
}

AUTHDATA_DREAMSCHOOL_ORG_MAP = {
  u'bar': {u'school1': 3, u'äö school': 1},
}

DS_DATA = {
  'id': 123,
  'username': u'user',
  'first_name': u'first',
  'last_name': u'last',
  'roles': [
    {
     'permissions': [{
       'code': authdata.datasources.dreamschool.TEACHER_PERM,
     }],
     'organisation': {'id': 1},
    },
  ],
  'user_groups': [
    {
      'organisation': {
          'id': 1,
          'title': u'Äö school',
      },
      'title': u'Group1',
    },
  ],
}

DS_EXPECTED = {
 'attributes': [],
 'first_name': u'first',
 'last_name': u'last',
 'roles': [{'group': u'Group1',
            'municipality': u'Bar',
            'role': u'teacher',
            'school': u'Äö school'}],
 'username': u'MPASSOID.ea5f9ca03f6edf5a0409d',
}


class TestAdminView(APITestCase):

  def setUp(self):
    self.user = f.UserFactory.create(is_superuser=True, is_staff=True)
    self.client.force_authenticate(user=self.user)

  def test_login_page(self):
    result = self.client.get('/sysadmin/')
    self.assertEqual(result.status_code, 302)


@override_settings(AUTH_EXTERNAL_SOURCES=AUTH_EXTERNAL_SOURCES)
@override_settings(AUTH_EXTERNAL_ATTRIBUTE_BINDING=AUTH_EXTERNAL_ATTRIBUTE_BINDING)
@override_settings(AUTH_EXTERNAL_MUNICIPALITY_BINDING=AUTH_EXTERNAL_MUNICIPALITY_BINDING)
@override_settings(AUTHDATA_DREAMSCHOOL_ORG_MAP=AUTHDATA_DREAMSCHOOL_ORG_MAP)
class TestHelpers(APITestCase):

  def test_get_external_user_data(self):
    with mock.patch('authdata.datasources.dreamschool.requests') as requests_mock:
      response_mock = mock.Mock()
      response_mock.status_code = 200
      response_mock.json.return_value = DS_DATA

      requests_mock.get.return_value = response_mock
      requests_mock.codes = requests.codes

      ext_user_data = authdata.views.get_external_user_data('dreamschool', '123')
      ext_user_data['roles'] = list(ext_user_data['roles'])

      self.assertEqual(ext_user_data, DS_EXPECTED)


@override_settings(AUTH_EXTERNAL_SOURCES=AUTH_EXTERNAL_SOURCES)
@override_settings(AUTH_EXTERNAL_ATTRIBUTE_BINDING=AUTH_EXTERNAL_ATTRIBUTE_BINDING)
@override_settings(AUTH_EXTERNAL_MUNICIPALITY_BINDING=AUTH_EXTERNAL_MUNICIPALITY_BINDING)
@override_settings(AUTHDATA_DREAMSCHOOL_ORG_MAP=AUTHDATA_DREAMSCHOOL_ORG_MAP)
@mock.patch('authdata.datasources.dreamschool.requests')
class TestQueryView(APITestCase):

  def setUp(self):
    self.request_factory = APIRequestFactory()
    self.user = f.UserFactory.create()

  def test_get_object_does_not_exist(self, requests_mock):
    request = self.request_factory.get('/api/1/users')
    force_authenticate(request, user=self.user)
    view = authdata.views.QueryView()
    view.kwargs = {'username': 'foo'}
    with self.assertRaises(django.http.Http404):
      view.get_object()

  def test_get_object_with_lookup(self, requests_mock):
    request = self.request_factory.get('/api/1/users')
    force_authenticate(request, user=self.user)
    view = authdata.views.QueryView()
    view.kwargs = {'username': self.user.username}
    view.request = request
    obj = view.get_object()
    self.assertEqual(obj, self.user)

  def test_get_user_does_not_exist(self, requests_mock):
    request = self.request_factory.get('/api/1/users')
    force_authenticate(request, user=self.user)
    view = authdata.views.QueryView.as_view()

    response = view(request, username='foo')

    self.assertEqual(response.status_code, 404)

  def test_get_user_exists(self, requests_mock):
    request = self.request_factory.get('/api/1/users')
    force_authenticate(request, user=self.user)
    view = authdata.views.QueryView.as_view()

    f.UserFactory.create(username='foo')
    response = view(request, username='foo')

    self.assertEqual(response.status_code, 200)

  def test_get_user_external_source_not_configured(self, requests_mock):
    request = self.request_factory.get('/api/1/users')
    force_authenticate(request, user=self.user)
    view = authdata.views.QueryView.as_view()

    self.user.external_source = 'doesntexist'
    self.user.external_id = 123
    self.user.save()

    response = view(request, username=self.user.username)

    self.assertEqual(response.status_code, 200)

  def test_get_user_external_source_cannot_import(self, requests_mock):
    request = self.request_factory.get('/api/1/users')
    force_authenticate(request, user=self.user)
    view = authdata.views.QueryView.as_view()

    self.user.external_source = 'doesntexist'
    self.user.external_id = 123
    self.user.save()

    with mock.patch('authdata.views.get_external_user_data') as ext_mock:
      ext_mock.side_effect = ImportError
      response = view(request, username=self.user.username)

    self.assertEqual(response.status_code, 200)
    self.assertEqual(response.data, None)

  def test_get_user_external_source_data_is_none(self, requests_mock):
    request = self.request_factory.get('/api/1/users')
    force_authenticate(request, user=self.user)
    view = authdata.views.QueryView.as_view()

    self.user.external_source = 'dreamschool'
    self.user.external_id = 123
    self.user.save()

    with mock.patch('authdata.views.get_external_user_data') as ext_mock:
      ext_mock.return_value = None
      response = view(request, username=self.user.username)

    self.assertEqual(response.status_code, 200)
    self.assertEqual(response.data, None)

  def test_get_user_external(self, requests_mock):
    ds_response_mock = mock.Mock()
    ds_response_mock.status_code = 200
    ds_response_mock.json.return_value = DS_DATA
    requests_mock.get.return_value = ds_response_mock
    requests_mock.codes = requests.codes

    request = self.request_factory.get('/api/1/users')
    force_authenticate(request, user=self.user)
    view = authdata.views.QueryView.as_view()

    self.user.external_source = 'dreamschool'
    self.user.external_id = 123
    self.user.save()

    attr = f.UserAttributeFactory(user=self.user)

    response = view(request, username=self.user.username)
    self.assertEqual(response.status_code, 200)
    response.data['roles'] = list(response.data['roles'])
    expected = DS_EXPECTED
    expected['attributes'] = [{'name': attr.attribute.name, 'value': attr.value}]
    self.assertEqual(response.data, expected)

  def test_get_user_fetch_external(self, requests_mock):
    ds_response_mock = mock.Mock()
    ds_response_mock.status_code = 200
    ds_response_mock.json.return_value = DS_DATA
    requests_mock.get.return_value = ds_response_mock
    requests_mock.codes = requests.codes

    request = self.request_factory.get('/api/1/users', {'dreamschool': 123})
    force_authenticate(request, user=self.user)
    view = authdata.views.QueryView.as_view()

    response = view(request)
    self.assertEqual(response.status_code, 200)
    response.data['roles'] = list(response.data['roles'])
    expected = DS_EXPECTED
    expected['attributes'] = [{'name': u'dreamschool', 'value': u'123'}]
    self.assertEqual(response.data, expected)

  def test_get_user_fetch_doesnt_exist(self, requests_mock):
    self.client.force_authenticate(user=self.user)

    with mock.patch('authdata.views.get_external_user_data', return_value=None):
      result = self.client.get('/api/1/user?dreamschool=123')

    self.assertEqual(result.status_code, 200, repr(result))
    self.assertEqual(result.data, None)

  def test_get_user_external_source_import_error(self, requests_mock):
    self.client.force_authenticate(user=self.user)

    with mock.patch('authdata.views.get_external_user_data', side_effect=ImportError):
      result = self.client.get('/api/1/user?dreamschool=123')

    self.assertEqual(result.status_code, 404, repr(result))

  def test_get_object_with_attributes(self, requests_mock):
    ds_response_mock = mock.Mock()
    ds_response_mock.status_code = 200
    ds_response_mock.json.return_value = DS_DATA
    requests_mock.codes = requests.codes
    requests_mock.get.return_value = ds_response_mock

    self.client.force_authenticate(user=self.user)
    f.UserAttributeFactory(user=self.user, attribute__name='foo', value='bar')
    result = self.client.get('/api/1/user?dreamschool=123&foo=bar&zao=zup')
    self.assertEqual(result.status_code, 404) # RR 200 -> 404

  def test_get_user_fetch_no_attribute_binding(self, requests_mock):
    ds_response_mock = mock.Mock()
    ds_response_mock.status_code = 200
    ds_response_mock.json.return_value = DS_DATA
    requests_mock.codes = requests.codes
    requests_mock.get.return_value = ds_response_mock

    self.client.force_authenticate(user=self.user)
    f.UserAttributeFactory(user=self.user, attribute__name='foo', value='bar')
    result = self.client.get('/api/1/user?foo=123&zao=zup')
    self.assertEqual(result.status_code, 404)

  def test_get_object_no_attributes(self, request_mock):
    self.client.force_authenticate(user=self.user)
    f.UserAttributeFactory(attribute__name='foo', value='bar')
    result = self.client.get('/api/1/user')
    self.assertEqual(result.status_code, 404)


class TestUserFilter(APITestCase):

  def test_timestamp_filter(self):
    obj = authdata.views.UserFilter()
    date = 0

    for _ in xrange(10):
      f.UserFactory()

    qs = authdata.models.User.objects.all()
    qs_out = obj.timestamp_filter(qs, date)
    self.assertTrue(qs_out is not None)

  def test_timestamp_filter_value_error(self):
    obj = authdata.views.UserFilter()
    qs = authdata.models.User.objects.all()
    qs_out = obj.timestamp_filter(queryset=qs, value='')
    self.assertEqual(type(qs_out.none()), type(qs_out))


@override_settings(AUTH_EXTERNAL_SOURCES=AUTH_EXTERNAL_SOURCES)
@override_settings(AUTH_EXTERNAL_ATTRIBUTE_BINDING=AUTH_EXTERNAL_ATTRIBUTE_BINDING)
@override_settings(AUTH_EXTERNAL_MUNICIPALITY_BINDING=AUTH_EXTERNAL_MUNICIPALITY_BINDING)
@override_settings(AUTHDATA_DREAMSCHOOL_ORG_MAP=AUTHDATA_DREAMSCHOOL_ORG_MAP)
@mock.patch('authdata.datasources.dreamschool.requests')
class TestUserViewSet(APITestCase):

  def setUp(self):
    self.request_factory = APIRequestFactory()
    self.user = f.UserFactory.create()
    self.client.force_authenticate(user=self.user)

  def test_list_user_data(self, requests_mock):
    ds_response_mock = mock.Mock()
    ds_response_mock.status_code = 200
    ds_response_mock.json.return_value = {'objects': [DS_DATA]}
    requests_mock.get.return_value = ds_response_mock
    requests_mock.codes = requests.codes

    response = self.client.get('/api/1/user/?municipality=Bar')
    self.assertEquals(response.status_code, 200)

  def test_list_import_error(self, requests_mock):
    with mock.patch('authdata.views.importlib') as importlib_mock:
      importlib_mock.import_module = mock.Mock()
      importlib_mock.import_module.side_effect = ImportError
      response = self.client.get('/api/1/user/?municipality=Bar')
    self.assertEquals(response.status_code, 200)


class TestAttributeViewSet(APITestCase):

  def setUp(self):
    self.user = f.UserFactory.create()
    self.client.force_authenticate(user=self.user)

  def test_list(self):
    attribute = f.AttributeFactory()
    result = self.client.get('/api/1/attribute/')
    self.assertEqual(result.status_code, 200, repr(result))
    self.assertEqual(result.data[0]['name'], attribute.name)

  def test_delete(self):
    attribute = f.AttributeFactory()
    result = self.client.delete('/api/1/attribute/%s/' % attribute.pk)
    # Not allowed. Read only
    self.assertEqual(result.status_code, 405)


class TestUserAttributeViewSet(APITestCase):

  def setUp(self):
    self.request_factory = APIRequestFactory()
    self.user = f.UserFactory.create()
    self.client.force_authenticate(user=self.user)

  def test_list(self):
    request = self.request_factory.get('/list')
    force_authenticate(request, user=self.user)
    view = authdata.views.UserViewSet.as_view({'get': 'list'})

    response = view(request)
    self.assertEquals(response.status_code, 200)

  def test_delete(self):
    user_attr = f.UserAttributeFactory()
    result = self.client.delete('/api/1/userattribute/%s/' % user_attr.pk)
    self.assertEqual(result.status_code, 204)


class TestMunicipalityViewSet(APITestCase):

  def setUp(self):
    self.user = f.UserFactory.create()
    self.client.force_authenticate(user=self.user)

  def test_list(self):
    muni = f.MunicipalityFactory()
    result = self.client.get('/api/1/municipality/')
    self.assertEqual(result.status_code, 200)
    self.assertEqual(result.data[0]['name'], muni.name)

  def test_delete(self):
    muni = f.MunicipalityFactory()
    result = self.client.delete('/api/1/municipality/%s/' % muni.pk)
    self.assertEqual(result.status_code, 204)


class TestSchoolViewSet(APITestCase):

  def setUp(self):
    self.user = f.UserFactory.create()
    self.client.force_authenticate(user=self.user)

  def test_list(self):
    school = f.SchoolFactory()
    result = self.client.get('/api/1/school/')
    self.assertEqual(result.status_code, 200)
    self.assertEqual(result.data[0]['name'], school.name)

  def test_delete(self):
    school = f.SchoolFactory()
    result = self.client.delete('/api/1/school/%s/' % school.pk)
    self.assertEqual(result.status_code, 204)


class TestRoleViewSet(APITestCase):

  def setUp(self):
    self.user = f.UserFactory.create()
    self.client.force_authenticate(user=self.user)

  def test_list(self):
    role = f.RoleFactory()
    result = self.client.get('/api/1/role/')
    self.assertEqual(result.status_code, 200)
    self.assertEqual(result.data[0]['name'], role.name)

  def test_delete(self):
    role = f.RoleFactory()
    result = self.client.delete('/api/1/role/%s/' % role.pk)
    # Not allowed. Read only
    self.assertEqual(result.status_code, 405)


class TestAttendanceViewSet(APITestCase):

  def setUp(self):
    self.user = f.UserFactory.create()
    self.client.force_authenticate(user=self.user)

  def test_list(self):
    attendance = f.AttendanceFactory()
    result = self.client.get('/api/1/attendance/')
    self.assertEqual(result.status_code, 200, repr(result))
    self.assertEqual(result.data[0]['group'], attendance.group)

  def test_delete(self):
    attendance = f.AttendanceFactory()
    result = self.client.delete('/api/1/attendance/%s/' % attendance.pk)
    self.assertEqual(result.status_code, 204, repr(result))

# vim: tabstop=2 expandtab shiftwidth=2 softtabstop=2

