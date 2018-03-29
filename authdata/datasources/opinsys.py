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

import logging
import hashlib
import requests

from django.conf import settings

from authdata.datasources.base import ExternalDataSource

LOG = logging.getLogger(__name__)

class OpinsysDataSource(ExternalDataSource):
    
  """
  An external user attribute source. The source is identified by a specific
  attribute name, which is configured in the project settings.

  This is a base class for all external data sources
  """

  def __init__(self, clientId, clientKey, tenantId, municipality, *args, **kwargs):
    LOG.debug('Invoke init')
    self.request = None
    self.tenantId = tenantId
    self.clientId = clientId
    self.clientKey = clientKey
    self.municipality = municipality

  def _get_roles(self, data):
    out = {}
    roleString = ''
    ##TODO: multiple schools/roles/groups are not properly supported ATM!
    if data['schools'] is not None and isinstance(data['schools'], list) is True:
      schools = data['schools'];
      for school in schools:
        out['school'] = school['name']
        for role in school['roles']:
          roleString = role
        for group in school['groups']:
          if group['type'].lower() == 'teaching group':
            out['group'] = group['name']
    out['municipality'] = self.municipality
    if roleString.lower() == 'student':
      out['role'] = 'oppilas'
    elif roleString.lower() == 'teacher':
      out['role'] = 'opettaja'
    yield out

  def get_oid(self, username):
    LOG.debug('Invoke get_oid')
    """
    Generate MPASS OID for user from the username

    Not needed if authentication source returns proper oid
    """
    return 'MPASSOID.{user_hash}'.format(user_hash=hashlib.sha1('opinsys'+self.tenantId + username).hexdigest())[:30]

  def get_data(self, external_id):
    import httplib, urllib, base64, os, json, pprint, time
    LOG.debug('Invoke get_data')
    auth = base64.encodestring('%s:%s' % (self.clientId, self.clientKey)).replace('\n', '')
    headers = {"Host": self.tenantId, "Authorization": "Basic %s" % auth }
    try:
        conn = httplib.HTTPSConnection('api.opinsys.fi')
        conn.request("GET", "/v3/users/_by_id/" + external_id, "", headers)
        response = conn.getresponse()
        data = json.load(response)
        conn.close()
    except Exception as e:
        print(e)

    attributes = [ ]
    roles = self._get_roles(data)

    # On Demand provisioning of the user
    oid = self.get_oid(external_id)
    self.provision_user(oid, external_id)

    return {
      'username': oid,
      'first_name': data['first_name'],
      'last_name': data['last_name'],
      'roles': roles,
      'attributes': attributes
    }

  def get_user_data(self, request):
    LOG.debug('Invoke get_user_data')
    """
    Query for a user listing.

    request: the request object containing GET-parameters for filtering the query
    """
    raise NotImplementedError

# vim: tabstop=2 expandtab shiftwidth=2 softtabstop=2

