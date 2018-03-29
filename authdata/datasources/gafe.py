# -*- coding: utf-8 -*-

# The MIT License (MIT)
#
# Copyright (c) 2015-2016 CSC - IT Center for Science, http://www.csc.fi
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

from __future__ import print_function, unicode_literals

import logging
import hashlib
import requests

from django.conf import settings

from authdata.datasources.base import ExternalDataSource

import argparse
import json

import httplib2

from apiclient import discovery
from oauth2client.service_account import ServiceAccountCredentials

LOG = logging.getLogger(__name__)

class GafeDataSource(ExternalDataSource):
    
  """
  An external user attribute source. The source is identified by a specific
  attribute name, which is configured in the project settings.
  This is a base class for all external data sources
  """

  def __init__(self, keyPath, adminPrincipal, municipality, *args, **kwargs):
    LOG.debug('Invoke init')
    self.request = None
    self.keyPath = keyPath
    self.adminPrincipal = adminPrincipal
    self.municipality = municipality

  def _get_roles(self, data):
    out = {}
    out['school'] = data['SchoolID']
    str = data['Role'].lower()
    if str == 'teacher':
      out['role'] = 'Opettaja'
    elif str == 'student':
      out['role'] = 'Oppilas'
#    out['role'] = data['Role'].title()
    out['group'] = data['Class']
    out['municipality'] = self.municipality
    yield out

  def get_data(self, external_id):
    scopes = ['https://www.googleapis.com/auth/admin.directory.user.readonly']
    credentials = ServiceAccountCredentials.from_json_keyfile_name(self.keyPath, scopes)
    delegated = credentials.create_delegated(self.adminPrincipal)
    from httplib2 import Http
    http_auth = delegated.authorize(Http())
    service = discovery.build('admin', 'directory_v1', http=http_auth)

    # Limit the response fields to only needed ones
    fields = "primaryEmail,customSchemas,name"

    req = service.users().get(userKey=external_id,
                         projection="full",
#                         customFieldMask="mpassData",
#                         viewType="domain_public",
                         fields=fields)
    resp = req.execute()
    # On Demand provisioning of the user
    oid = self.get_oid(external_id)
    self.provision_user(oid, external_id)
    attributes = [ ]
    roles = [ ]
    if 'customSchemas' in resp and resp['customSchemas'] is not None:
        if 'PrimusV2' in resp['customSchemas'] and resp['customSchemas']['PrimusV2'] is not None:
            roles = self._get_roles(resp['customSchemas']['PrimusV2'])
            attributes = [{'name':'legacyId', 'value': resp['customSchemas']['PrimusV2']['PrimusID']}]
    return {
      'username': oid,
      'first_name': resp['name']['givenName'],
      'last_name': resp['name']['familyName'],
      'roles': roles,
      'attributes': attributes
    }

  def get_oid(self, username):
    LOG.debug('Invoke get_oid')
    """
    Generate MPASS OID for user from the username
    Not needed if authentication source returns proper oid
    """
    return 'MPASSOID.{user_hash}'.format(user_hash=hashlib.sha1('gafe' + username).hexdigest())[:30]

  def get_user_data(self, request):
    LOG.debug('Invoke get_user_data')
    """
    Query for a user listing.
    request: the request object containing GET-parameters for filtering the query
    """
    raise NotImplementedError
