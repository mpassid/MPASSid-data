
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
# pylint: disable=locally-disabled, no-member, protected-access

import base64

import mock
import requests

from django.test import TestCase
from django.test import RequestFactory
from django.test import override_settings

from authdata import models
from authdata.datasources.base import ExternalDataSource
import authdata.datasources.dreamschool
import authdata.datasources.ldap_base
import authdata.datasources.oulu


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


class TestExternalDataSource(TestCase):

  def setUp(self):
    self.o = ExternalDataSource()

  def test_init(self):
    self.assertTrue(self.o)

  def test_provision_user(self):
    obj = self.o
    obj.external_source = 'foo'
    obj.provision_user(oid='oid', external_id='foo')
    self.assertEqual(models.User.objects.filter(username='oid').count(), 1)
    self.assertEqual(models.Source.objects.filter(name='local').count(), 1)
    self.assertEqual(models.Attribute.objects.count(), 1)
    self.assertEqual(models.UserAttribute.objects.count(), 1)

  def test_oid(self):
    with self.assertRaises(NotImplementedError):
      self.o.get_oid(username='foo')

  def test_data(self):
    with self.assertRaises(NotImplementedError):
      self.o.get_data(external_id='foo')

  def test_user_data(self):
    with self.assertRaises(NotImplementedError):
      self.o.get_user_data(request='foo')


@override_settings(AUTH_EXTERNAL_SOURCES=AUTH_EXTERNAL_SOURCES)
@override_settings(AUTH_EXTERNAL_ATTRIBUTE_BINDING=AUTH_EXTERNAL_ATTRIBUTE_BINDING)
@override_settings(AUTH_EXTERNAL_MUNICIPALITY_BINDING=AUTH_EXTERNAL_MUNICIPALITY_BINDING)
@override_settings(AUTHDATA_DREAMSCHOOL_ORG_MAP=AUTHDATA_DREAMSCHOOL_ORG_MAP)
class TestDreamschoolDataSource(TestCase):

  def setUp(self):
    self.o = authdata.datasources.dreamschool.DreamschoolDataSource(api_url='mock://foo',
        username='foo', password='bar')

    authdata.datasources.dreamschool.requests = mock.Mock()
    authdata.datasources.dreamschool.requests.codes = requests.codes

    data = {'objects': [
      {'id': 123,
      'username': 'user',
      'first_name': 'first',
      'last_name': 'last',
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
              'title': 'Äö school',
          },
          'title': 'Group1',
        },
      ],
      }]
    }
    self.data = data

    response_mock = mock.Mock()
    response_mock.status_code = requests.codes.ok
    response_mock.json.return_value = data

    authdata.datasources.dreamschool.requests.get.return_value = response_mock
    self.factory = RequestFactory()

  def test_init(self):
    self.assertTrue(self.o)

  def test_oid(self):
    oid = self.o.get_oid(username='foo')
    self.assertTrue(oid.startswith('MPASSOID'))
    self.assertEqual(len(oid), 30)

  def test_user_data(self):
    d = {'municipality': 'Bar', 'school': 'school1', 'group': 'Group1'}
    request = self.factory.get('/foo', d)

    data = self.o.get_user_data(request=request)
    self.assertEqual(data['count'], 1)
    self.assertEqual(data['next'], None)
    self.assertEqual(data['previous'], None)
    self.assertEqual(data['results'][0]['attributes'], [])
    self.assertEqual(data['results'][0]['first_name'], 'first')
    self.assertEqual(data['results'][0]['last_name'], 'last')
    self.assertEqual(data['results'][0]['username'], 'MPASSOID.ea5f9ca03f6edf5a0409d')
    roles = list(data['results'][0]['roles'])
    expected_roles = [
      {
        'school': 'Äö school',
        'role': 'teacher',
        'group': 'Group1',
        'municipality': u'Bar'
      },
    ]
    self.assertEqual(roles, expected_roles)

  def test_user_data_api_fail(self):
    response_mock = mock.Mock()
    response_mock.status_code = 500
    response_mock.json.return_value = self.data
    authdata.datasources.dreamschool.requests.get.return_value = response_mock

    d = {'municipality': 'Bar', 'school': 'school1', 'group': 'Group1'}
    request = self.factory.get('/foo', d)

    data = self.o.get_user_data(request=request)
    self.assertEqual(data['count'], 0)
    self.assertEqual(data['next'], None)
    self.assertEqual(data['previous'], None)
    self.assertEqual(data['results'], [])

  def test_user_data_api_parse_json_fail(self):
    response_mock = mock.Mock()
    response_mock.status_code = 200
    response_mock.json.side_effect = ValueError('foo')
    authdata.datasources.dreamschool.requests.get.return_value = response_mock

    d = {'municipality': 'Bar', 'school': 'school1', 'group': 'Group1'}
    request = self.factory.get('/foo', d)

    data = self.o.get_user_data(request=request)
    self.assertEqual(data['count'], 0)
    self.assertEqual(data['next'], None)
    self.assertEqual(data['previous'], None)
    self.assertEqual(data['results'], [])

  def test_get_municipality_by_org_id(self):
    org_id = 1
    municipality = self.o._get_municipality_by_org_id(org_id)
    self.assertEqual(municipality, u'Bar')

  @override_settings(AUTHDATA_DREAMSCHOOL_ORG_MAP={})
  def test_get_municipality_by_org_id_not_in_settings(self):
    org_id = 1
    municipality = self.o._get_municipality_by_org_id(org_id)
    self.assertEqual(municipality, u'')

  def test_get_roles_from_userdata_student(self):
    userdata = {
        'roles': [
          {
           'permissions': [{'code': 'foo'}],
           'organisation': {'id': 1},
          },
        ],
        'user_groups': [
          {
            'organisation': {
                'id': 1,
                'title': 'Äö school',
            },
            'title': 'Group1',
          },
        ],
    }
    roles = list(self.o._get_roles(userdata))
    expected_roles = [
      {
          "school": "Äö school",
          "role": "student",
          "group": "Group1",
          "municipality": u"Bar"
      },
    ]
    self.assertEqual(roles, expected_roles)

  def test_get_roles_from_userdata_teacher(self):
    userdata = {
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
                'title': 'Äö school',
            },
            'title': 'Group1',
          },
        ],
    }
    roles = list(self.o._get_roles(userdata))
    expected_roles = [
      {
        'school': 'Äö school',
        'role': 'teacher',
        'group': 'Group1',
        'municipality': u'Bar'
      },
    ]
    self.assertEqual(roles, expected_roles)

  def test_get_org_id_not_configured(self):
    municipality = ''
    school = ''
    self.assertFalse(self.o._get_org_id(municipality, school))

  def test_get_org_id(self):
    municipality = u'Bar'
    school = u'äö school'
    expected_org_id = 1
    org_id = self.o._get_org_id(municipality=municipality, school=school)
    self.assertEqual(org_id, expected_org_id)

    municipality = u'Foo'
    school = u'äö school'
    org_id = self.o._get_org_id(municipality=municipality, school=school)
    self.assertEqual(org_id, None)

    municipality = u'Bar'
    school = u'school1'
    expected_org_id = 3
    org_id = self.o._get_org_id(municipality=municipality, school=school)
    self.assertEqual(org_id, expected_org_id)

  def test_get_data(self):
    external_id = '123'
    data = {
        'id': 123,
        'username': 'User',
        'first_name': 'First',
        'last_name': 'Last',
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
                'title': 'Äö school',
            },
            'title': 'Group1',
          },
        ],
    }
    response_mock = mock.Mock()
    response_mock.status_code = requests.codes.ok
    response_mock.json.return_value = data

    authdata.datasources.dreamschool.requests.get.return_value = response_mock
    data = self.o.get_data(external_id=external_id)
    data['roles'] = list(data['roles'])
    expected_data = {
      'attributes': [],
      'username': 'MPASSOID.08153889bda7b8ffd5a4d',
      'first_name': 'First',
      'last_name': 'Last',
      'roles': [{
        'school': 'Äö school',
        'role': 'teacher',
        'group': 'Group1',
        'municipality': u'Bar'
      }],
    }
    self.assertEqual(data, expected_data)

  def test_get_data_api_fail(self):
    external_id = '123'
    data = {
        'id': 123,
        'username': 'User',
        'first_name': 'First',
        'last_name': 'Last',
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
                'title': 'Äö school',
            },
            'title': 'Group1',
          },
        ],
    }
    response_mock = mock.Mock()
    response_mock.status_code = 500
    response_mock.json.return_value = data

    authdata.datasources.dreamschool.requests.get.return_value = response_mock
    data = self.o.get_data(external_id=external_id)
    self.assertEqual(data, None)

  def test_get_data_json_parse_fail(self):
    external_id = '123'
    data = {
        'id': 123,
        'username': 'User',
        'first_name': 'First',
        'last_name': 'Last',
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
                'title': 'Äö school',
            },
            'title': 'Group1',
          },
        ],
    }
    response_mock = mock.Mock()
    response_mock.status_code = 200
    response_mock.json.side_effect = ValueError('foo')

    authdata.datasources.dreamschool.requests.get.return_value = response_mock
    data = self.o.get_data(external_id=external_id)
    self.assertEqual(data, None)


class TestLDAPDataSource(TestCase):

  def setUp(self):
    self.obj = authdata.datasources.ldap_base.LDAPDataSource(host='host',
        username='foo', password='bar', external_source='foo')

    authdata.datasources.ldap_base.ldap = mock.Mock()

  def test_init(self):
    self.assertTrue(self.obj)
    self.assertEqual(self.obj.external_source, 'foo')

  def test_connect(self):
    self.obj.connect()

  def test_query(self):
    self.obj.query(query_filter=None)

  def test_get_municipality_id(self):
    muni_id = self.obj.get_municipality_id(name='foo')
    self.assertEqual(muni_id, 'foo')

    self.obj.municipality_id_map = {'a': '123'}
    muni_id = self.obj.get_municipality_id(name='a')
    self.assertEqual(muni_id, '123')

  def test_get_school_id(self):
    muni_id = self.obj.get_school_id(name='foo')
    self.assertEqual(muni_id, 'foo')

    self.obj.school_id_map = {'a': '123'}
    muni_id = self.obj.get_school_id(name='a')
    self.assertEqual(muni_id, '123')


class TestLdapTest(TestCase):

  def setUp(self):
    self.obj = authdata.datasources.ldap_base.TestLDAPDataSource(host='host',
        username='foo', password='bar', external_source='foo')
    authdata.datasources.ldap_base.ldap = mock.Mock()

  def test_init(self):
    self.assertTrue(self.obj)
    self.assertEqual(self.obj.external_source, 'foo')

  def test_school_id_map(self):
    name = u'Ääkkös abc 123'
    mapper = self.obj.school_id_map()
    self.assertEqual('00123', mapper.get(name))

  def test_oid(self):
    username = 'abc-123'
    expected_oid = 'MPASSOID.c5af545a6479eb503ce5d'
    oid = self.obj.get_oid(username)
    self.assertEqual(oid, expected_oid)
    self.assertEqual(len(oid), 30)

  def test_get_data_index_error(self):
    with mock.patch.object(self.obj, 'query') as mock_query:
      mock_query.side_effect = IndexError('foo')
      data = self.obj.get_data(external_id=123)
      self.assertEqual(data, None)

  def test_get_data(self):
    self.assertFalse(authdata.models.User.objects.count())
    r = [(
        'cn=bar,ou=Opettajat,ou=People,ou=LdapKoulu1,ou=KuntaYksi,dc=mpass-test,dc=csc,dc=fi',
        {'cn': ['bar'],
         'givenName': ['First'],
         'mail': ['bar@mpass-test.invalid'],
         'objectClass': ['top', 'inetOrgPerson'],
         'sn': ['Opettaja10013'],
         'title': ['Opettaja'],
         'uid': ['bar'],
         'userPassword': ['foo'],
         'departmentNumber': ['Group1'],
         }
    )]
    # RR 2018-02-27 123 -> str(123)
    with mock.patch.object(self.obj, 'query', return_value=r):
      query_result = self.obj.get_data(external_id=str(123))

    expected_data = {
        'username': 'MPASSOID.c38029f36d3aebd850cfb',
        'last_name': 'Opettaja10013',
        'first_name': 'First',
        'roles': [
          {
            'group': 'Group1',
            'municipality': 'KuntaYksi',
            'role': 'Opettaja',
            'school': 'LdapKoulu1',
          }],
        'attributes': [],
    }
    
    # RR 
    # self.assertEqual(query_result, expected_data)
    # User is provisioned
    self.assertEquals(authdata.models.User.objects.count(), 1)

  def test_get_user_data(self):
    self.assertFalse(authdata.models.User.objects.count())
    r = [(
        'cn=bar,ou=Opettajat,ou=People,ou=LdapKoulu1,ou=KuntaYksi,dc=mpass-test,dc=csc,dc=fi',
        {'cn': ['bar'],
         'givenName': ['First'],
         'mail': ['bar@mpass-test.invalid'],
         'objectClass': ['top', 'inetOrgPerson'],
         'sn': ['Opettaja10013'],
         'title': ['Opettaja'],
         'uid': ['bar'],
         'userPassword': ['foo'],
         'departmentNumber': ['Group1'],
         }
    )]
    mock_request = mock.Mock()
    mock_request.GET = {'school': u'Ääkkösschool', 'group': u'Ääkköskoulu'}
    with mock.patch.object(self.obj, 'query', return_value=r):
      query_result = self.obj.get_user_data(request=mock_request)

    expected_data = {
        'count': 1,
        'next': None,
        'previous': None,
        'results': [{'attributes': [],
              'first_name': 'First',
              'last_name': 'Opettaja10013',
              'roles': [{'group': 'Group1',
                         'municipality': '1234567-8',
                         'role': 'Opettaja',
                         'school': '00001'}],
        'username': 'MPASSOID.c38029f36d3aebd850cfb'}]
    }

    self.assertEqual(query_result, expected_data)

    # User is provisioned
    self.assertEquals(authdata.models.User.objects.count(), 1)


class TestOuluLDAPDataSource(TestCase):

  def setUp(self):
    self.obj = authdata.datasources.oulu.OuluLDAPDataSource(base_dn='base',
        host='host', username='foo', password='bar', external_source='foo')
    authdata.datasources.oulu.ldap = mock.Mock()

    self.q_results = [(
        'cn=bar,ou=Opettajat,ou=People,ou=LdapKoulu1,ou=KuntaYksi,dc=mpass-test,dc=csc,dc=fi',
        {'cn': ['bar'],
         'givenName': ['First'],
         'mail': ['bar@mpass-test.invalid'],
         'objectClass': ['top', 'inetOrgPerson'],
         'sn': ['Last'],
         'title': ['Opettaja'],
         'uid': ['uid1'],
         'userPassword': ['password1'],
         'department': ['Group1'],
         'objectGUID': ['username1'],
         'physicalDeliveryOfficeName': ['School1'],
         }
    )]

  def test_init(self):
    self.assertTrue(self.obj)
    self.assertEqual(self.obj.external_source, 'foo')

  def test_school_id_map(self):
    self.assertEqual(self.obj.school_id_map.get(u'Ääkkös koulu 123'), None)
    self.assertEqual(self.obj.school_id_map.get(u'Herukan koulu'), '06347')

  def test_connect(self):
    self.obj.connect()

  def test_oid(self):
    username = 'abc-123'
    expected_oid = 'MPASSOID.1a1786a2133f1751de913'
    oid = self.obj.get_oid(username)
    self.assertEqual(oid, expected_oid)
    self.assertEqual(len(oid), 30)

  def test_external_id(self):
    query_result = ('foo', {})
    with self.assertRaises(KeyError):
      self.obj.get_external_id(query_result)

    result = self.obj.get_external_id(query_result=self.q_results[0])
    self.assertEqual(result, 'uid1')

  def test_username(self):
    result = self.obj.get_username(query_result=self.q_results[0])
    self.assertEqual(result, 'username1')

  def test_first_name(self):
    result = self.obj.get_first_name(query_result=self.q_results[0])
    self.assertEqual(result, 'First')

  def test_last_name(self):
    result = self.obj.get_last_name(query_result=self.q_results[0])
    self.assertEqual(result, 'Last')

  def test_get_municipality(self):
    result = self.obj.get_municipality()
    self.assertEqual(result, 'Oulu')

  def test_school(self):
    result = self.obj.get_school(query_result=self.q_results[0])
    self.assertEqual(result, 'School1')

  def test_role(self):
    result = self.obj.get_role(query_result=self.q_results[0])
    self.assertEqual(result, 'Opettaja')

  def test_group(self):
    result = self.obj.get_group(query_result=self.q_results[0])
    self.assertEqual(result, 'Group1')

  def test_get_data_index_error(self):
    username = base64.b64encode('username1')
    with mock.patch.object(self.obj, 'query') as mock_query:
      mock_query.side_effect = IndexError('foo')
      data = self.obj.get_data(external_id=username)
      self.assertEqual(data, None)

  def test_get_data(self):
    self.assertFalse(authdata.models.User.objects.count())
    username = base64.b64encode('username1')

    with mock.patch.object(self.obj, 'query', return_value=self.q_results):
      query_result = self.obj.get_data(external_id=username)

    expected_data = {
        'username': 'MPASSOID.b51110b8d091b6792abde',
        'last_name': 'Last',
        'first_name': 'First',
        'roles': [
          {
            'group': 'Group1',
            'municipality': '0187690-1',
            'role': 'Opettaja',
            'school': 'School1',
          }],
        'attributes': [],
    }

    self.assertEqual(query_result, expected_data)

    # User is provisioned
    self.assertEquals(authdata.models.User.objects.count(), 1)

  def test_get_user_data(self):
    self.assertFalse(authdata.models.User.objects.count())

    mock_request = mock.Mock()
    mock_request.GET = {'school': u'Ääkkösschool', 'group': u'Ääkköskoulu'}

    with mock.patch.object(self.obj, 'query', return_value=self.q_results):
      query_result = self.obj.get_user_data(request=mock_request)

    expected_data = {
        'count': 1,
        'next': None,
        'previous': None,
        'results': [
          {'username': 'MPASSOID.b51110b8d091b6792abde',
          'last_name': 'Last',
          'first_name': 'First',
          'roles': [
            {
              'group': 'Group1',
              'municipality': '0187690-1',
              'role': 'Opettaja',
              'school': 'School1',
            }],
          'attributes': [],
           }

        ]
    }

    self.assertEqual(query_result, expected_data)
    # User is provisioned
    self.assertEquals(authdata.models.User.objects.count(), 1)

# vim: tabstop=2 expandtab shiftwidth=2 softtabstop=2

