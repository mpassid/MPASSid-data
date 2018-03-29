
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

"""
Dreamschool external data source
"""

import logging
import hashlib
import requests

from django.conf import settings

from authdata.datasources.base import ExternalDataSource

LOG = logging.getLogger(__name__)

# Example response from Dreamschool
# {
#    "meta": {
#        "limit": 0,
#        "offset": 0,
#        "total_count": 1
#    },
#    "objects": [
#        {
#            "email": "foo.bar@unelmakoulu.fi",
#            "first_name": "Foo",
#            "id": "123",
#            "last_name": "Bar",
#            "organisations": [
#                {
#                    "created": "2014-03-12T19:21:47.403524",
#                    "id": "3",
#                    "modified": "2015-08-10T12:37:54.719312",
#                    "name": "Organisation",
#                    "override_username_cleanup": false,
#                    "registration_allowed": false,
#                    "resource_uri": "/api/2/organisation/3/",
#                    "source": "zap",
#                    "title": "Organisation Name"
#                }
#            ],
#            "phone_number": "+3581234567",
#            "picture_url": "https://id.dreamschool.fi/media/avatar/foo.png",
#            "resource_uri": "/api/2/user/123/",
#            "roles": [
#                {
#                    "created": "2014-03-12T19:21:47.403524",
#                    "id": "1",
#                    "modified": "2015-10-13T14:10:54.732225",
#                    "name": "teacher",
#                    "official": true,
#                    "organisation": {
#                        "created": "2014-03-12T19:21:47.403524",
#                        "id": "3",
#                        "modified": "2015-08-10T12:37:54.719312",
#                        "name": "foo",
#                        "override_username_cleanup": false,
#                        "registration_allowed": false,
#                        "resource_uri": "/api/2/organisation/3/",
#                        "source": "zap",
#                        "title": "Organisation Name"
#                    },
#                    "permissions": [
#                        {
#                            "code": "dreamdiary.diary.supervisor",
#                            "id": "12",
#                            "name": "dreamdiary",
#                            "resource_uri": ""
#                        },
#                    ],
#                    "resource_uri": "/api/2/role/1/",
#                    "source": "zap",
#                    "title": "teacher"
#                }
#            ],
#            "theme_color": "ffffff",
#            "user_groups": [
#                {
#                    "created": "2014-03-12T19:21:47.403524",
#                    "filter_type": null,
#                    "id": "2",
#                    "level": 0,
#                    "lft": 1,
#                    "modified": "2014-03-12T19:21:47.403524",
#                    "name": "1a",
#                    "official": false,
#                    "organisation": {
#                        "created": "2014-03-12T19:21:47.403524",
#                        "id": "3",
#                        "modified": "2015-08-10T12:37:54.719312",
#                        "name": "foo",
#                        "override_username_cleanup": false,
#                        "registration_allowed": false,
#                        "resource_uri": "/api/2/organisation/3/",
#                        "source": "zap",
#                        "title": "Organisation Name"
#                    },
#                    "resource_uri": "/api/2/group/2/",
#                    "rght": 2,
#                    "source": "",
#                    "title": "1a",
#                    "tree_id": 150
#                },
#            ],
#            "username": "foo.bar"
#        },
#    ]
# }

TEACHER_PERM = 'dreamdiary.diary.supervisor'


class DreamschoolDataSource(ExternalDataSource):
  """
  Required configuration parameters:
    api_url
    username
    password
  """

  external_source = 'dreamschool'

  def __init__(self, api_url, username, password, *args, **kwargs):
    self.request = None
    self.api_url = api_url
    self.username = username
    self.password = password

  # PRIVATE METHODS
  def _get_municipality_by_org_id(self, org_id):
    org_id = int(org_id)
    LOG.debug('Fetching municipality for org_id',
              extra={'data': {'org_id': org_id}})
    for municipality in settings.AUTHDATA_DREAMSCHOOL_ORG_MAP.keys():
      for org_title in settings.AUTHDATA_DREAMSCHOOL_ORG_MAP[municipality]:
        if int(settings.AUTHDATA_DREAMSCHOOL_ORG_MAP[municipality][org_title]) == org_id:
          return municipality.capitalize()
    return u''

  def _get_roles(self, user_data):
    """Create roles structure

    Example of output::

      [
          {
              "school": "17392",
              "role": "teacher",
              "group": "7A",
              "municipality": "City"
          },
          {
              "school": "17392",
              "role": "teacher",
              "group": "7B",
              "municipality": "City"
          }
      ]
    """

    roles_data = user_data['roles']
    groups_data = user_data['user_groups']

    # First we get list of schools where user is a teacher
    schools_as_teacher = []
    for r in roles_data:
      org_id = r['organisation']['id']
      if TEACHER_PERM in [i['code'] for i in r['permissions']]:
        schools_as_teacher.append(org_id)

    # iterate through groups
    for g in groups_data:
      out = {}
      out['school'] = g['organisation']['title']
      if g['organisation']['id'] in schools_as_teacher:
        out['role'] = 'teacher'
      else:
        out['role'] = 'student'
      out['group'] = g['title']
      out['municipality'] = self._get_municipality_by_org_id(g['organisation']['id'])
      yield out

  def _get_org_id(self, municipality, school):
    if not municipality or not school:
      return None

    LOG.debug('Fetching org id for given municipality and school',
              extra={'data': {'municipality': repr(municipality),
              'school': repr(school)}})

    try:
      muni = settings.AUTHDATA_DREAMSCHOOL_ORG_MAP[municipality.lower()]
    except KeyError:
      LOG.error('Unknown municipality')
      return None

    try:
      org_id = muni[school.lower()]
    except KeyError:
      LOG.error('Unknown school', extra={'data':
        {'school': repr(school),
         'municipality': repr(municipality),
         'muni_data': repr(muni),
         }})
      return None

    LOG.debug('Mapped municipality and school to org id', extra={'data': {
      'municipality': repr(municipality),
      'school': repr(school),
      'org_id': org_id,
    }})
    return org_id

  # INTERFACE METHODS
  def get_oid(self, username):
    """
    There is no OID information in this external source. Generate fake OID
    from username.
    """
    # TODO: OID is cut to 30 chars due to django username limitation
    return 'MPASSOID.{user_hash}'.format(user_hash=hashlib.sha1('dreamschool' + username).hexdigest())[:30]

  def get_user_data(self, request):
    """
    Requested by mpass-connector

    Returns a list of users based on request.GET filtering values
    """

    self.request = request
    school = u''
    group = u''
    municipality = request.GET['municipality'].lower()

    if 'school' in request.GET:
      school = unicode(request.GET['school'])
    if 'group' in request.GET:
      group = unicode(request.GET['group'])

    url = self.api_url
    username = self.username
    password = self.password
    org_id = self._get_org_id(municipality, school)

    params = {}
    if org_id:
      params = {
        'organisations__id': org_id,
      }
      if group:
        params['user_groups__title__icontains'] = group
      r = requests.get(url, auth=(username, password), params=params)
    else:
      # This may fail to proxy timeout error
      # TODO: Catch status code 502 Proxy error
      r = requests.get(url, auth=(username, password))

    LOG.debug('Fetched from dreamschool', extra={'data':
      {'api_url': self.api_url,
       'params': params,
       'status_code': r.status_code,
       }})

    if r.status_code != requests.codes.ok:
      LOG.warning('Dreamschool API response not OK', extra={'data':
        {'status_code': r.status_code,
         'municipality': repr(municipality),
         'api_url': self.api_url,
         'username': self.username,
         'params': params,
         }})
      return {
        'count': 0,
        'next': None,
        'previous': None,
        'results': [],
      }

    response = []
    user_data = {}
    try:
      user_data = r.json()
    except ValueError:
      LOG.exception('Could not parse user data from dreamschool API')
      return {
        'count': 0,
        'next': None,
        'previous': None,
        'results': [],
      }

    for d in user_data['objects']:
      user_id = d['id']
      username = d['username']
      first_name = d['first_name']
      last_name = d['last_name']
      oid = self.get_oid(username)
      external_id = str(user_id)
      attributes = [
      ]
      roles = self._get_roles(d)
      response.append({
        'username': oid,
        'first_name': first_name,
        'last_name': last_name,
        'roles': roles,
        'attributes': attributes
      })

      # On Demand provisioning of the users
      self.provision_user(oid, external_id)

    # TODO: support actual paging via SimplePagedResultsControl
    return {
      'count': len(response),
      'next': None,
      'previous': None,
      'results': response,
    }

  def get_data(self, external_id):
    """Requested by idP

    external_id: user id in dreamschool
    """
    url = self.api_url + external_id + '/'  # TODO: use join
    username = self.username
    password = self.password

    r = requests.get(url, auth=(username, password))

    LOG.debug('Fetched from dreamschool', extra={'data':
      {'url': url,
       'status_code': r.status_code,
       }})

    if r.status_code != requests.codes.ok:
      LOG.warning('Dreamschool API response not OK', extra={'data':
        {'status_code': r.status_code,
         'url': url,
         'username': self.username,
         }})
      return None

    user_data = {}
    try:
      user_data = r.json()
    except ValueError:
      LOG.exception('Could not parse user data from dreamschool API')
      return None

    d = user_data
    username = d['username']
    first_name = d['first_name']
    last_name = d['last_name']
    attributes = [
    ]
    roles = self._get_roles(d)

    # On Demand provisioning of the user
    external_id = str(d['id'])
    oid = self.get_oid(username)
    self.provision_user(oid, external_id)

    return {
      'username': self.get_oid(username),
      'first_name': first_name,
      'last_name': last_name,
      'roles': roles,
      'attributes': attributes
    }
    # TODO: support actual paging via SimplePagedResultsControl

# vim: tabstop=2 expandtab shiftwidth=2 softtabstop=2

